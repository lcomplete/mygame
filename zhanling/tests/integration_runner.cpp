#include "integration_runner.h"
#include "actors/actor_visual.h"
#include "actors/enemy.h"
#include "actors/player.h"
#include "core/game.h"
#include "world/world.h"
#include <godot_cpp/classes/config_file.hpp>
#include <godot_cpp/classes/input.hpp>
#include <godot_cpp/classes/image.hpp>
#include <godot_cpp/classes/scene_tree.hpp>
#include <godot_cpp/variant/utility_functions.hpp>
using namespace godot;
namespace zhan {
bool IntegrationRunner::expect(bool condition, const char* message) {
    UtilityFunctions::print(condition ? "PASS: " : "FAIL: ", message);
    if (!condition) {
        ++failures;
        game.get_tree()->quit(1);
    }
    return condition;
}
void IntegrationRunner::next() {
    ++step;
    frames = 0;
    waited = 0;
}
struct JumpCase {
    int room;
    Vector2 from, to;
};
static const JumpCase ROUTES[] = {
    {0, {665, 610}, {925, 610}},   {1, {1100, 610}, {1460, 515}}, {2, {730, 510}, {930, 455}},
    {2, {1660, 440}, {1820, 355}}, {2, {1880, 355}, {2140, 440}}, {4, {415, 610}, {540, 510}},
    {4, {580, 510}, {780, 415}},   {4, {820, 415}, {1035, 325}},  {4, {1095, 325}, {1310, 240}}};
void IntegrationRunner::update(float dt) {
    if (failures)
        return;
    ++frames;
    waited += dt;
    auto* input = Input::get_singleton();
    if (step == 0) {
        if (frames < 5)
            return;
        expect(game.data.rooms.size() == 5, "five campaign chapters loaded");
        bool character_art_valid = true;
        for (const char* kind : {"ninja", "soldier", "archer", "magistrate", "scribe"}) {
            for (const auto& clip : std::vector<std::pair<String, int>>{
                     {"idle", 2}, {"run", 6}, {"jump", 1}, {"attack", 3}, {"dash", 1}}) {
                for (int i = 0; i < clip.second; ++i) {
                    Ref<Texture2D> texture = ActorVisual::load_frame(kind, clip.first, i);
                    if (texture.is_null() || !texture->get_path().ends_with(".tres")) {
                        character_art_valid = false;
                        continue;
                    }
                    Ref<Image> image = texture->get_image();
                    character_art_valid = character_art_valid && image.is_valid() &&
                                          !image->is_empty() && image->detect_alpha() != Image::ALPHA_NONE &&
                                          image->get_used_rect().size.x > 0;
                }
            }
        }
        if (!expect(character_art_valid, "all 65 redesigned character frames load with transparent artwork"))
            return;
        game.begin(false);
        next();
    } else if (step == 1) {
        expect(game.screen == Screen::Dialogue, "new game starts with narrative");
        while (game.screen == Screen::Dialogue) {
            game.ui->complete_line();
            game.advance_dialogue();
        }
        initial = game.world->get_player()->get_position();
        input->action_press("move_right");
        next();
    } else if (step == 2 && waited > .3f) {
        input->action_release("move_right");
        expect(game.world->get_player()->get_position().x > initial.x + 35, "movement uses engine physics");
        next();
    } else if (step == 3 && waited > .25f) {
        initial = game.world->get_player()->get_position();
        input->action_press("jump");
        next();
    } else if (step == 4 && waited > .12f) {
        expect(game.world->get_player()->get_position().y < initial.y - 35, "jump rises above the roof");
        input->action_release("jump");
        next();
    } else if (step == 5 && waited > .8f) {
        auto* p = game.world->get_player();
        expect(p->is_on_floor(), "player lands on authored collision geometry");
        int old = p->health();
        p->hurt(1, p->get_position() + Vector2(-10, 0));
        p->hurt(1, p->get_position() + Vector2(-10, 0));
        expect(p->health() == old - 1, "overlapping damage observes invulnerability");
        p->restore();
        initial = p->get_position();
        input->action_press("dash");
        next();
    } else if (step == 6 && waited > .05f) {
        auto* p = game.world->get_player();
        int hp = p->health();
        p->hurt(1, p->get_position() + Vector2(10, 0));
        expect(p->health() == hp && p->dashing(), "dash is invulnerable");
        input->action_release("dash");
        next();
    } else if (step == 7 && waited > .22f) {
        auto* world = game.world;
        auto* p = world->get_player();
        auto* e = world->get_enemies()[0];
        p->set_position(e->get_position() + Vector2(-62, 0));
        p->set_velocity(Vector2());
        input->action_press("attack");
        next();
    } else if (step == 8 && waited > .08f) {
        input->action_release("attack");
        expect(!game.world->get_enemies()[0]->alive(), "real attack input defeats a guard");
        auto* world = game.world;
        Vector2 seal = world->get_room().seals[0];
        world->strike(Rect2(seal - Vector2(100, 100), Vector2(200, 200)), 1);
        expect(world->remaining_seals() == 0, "sword cuts the physical seal");
        for (auto* e : world->get_enemies())
            if (e->alive())
                e->hurt(99, e->get_position() - Vector2(100, 0));
        expect(world->clear(), "exit unlocks only after guards and seals are cleared");
        game.set_screen(Screen::Paused);
        initial = world->get_player()->get_position();
        input->action_press("move_right");
        next();
    } else if (step == 9 && waited > .15f) {
        expect(game.world->get_player()->get_position().distance_to(initial) < .01,
               "pause freezes simulation");
        input->action_release("move_right");
        game.load_room(1, false);
        next();
    } else if (step == 10 && waited > .08f) {
        expect(game.world->remaining_enemies() == 5, "second chapter spawns authored encounters");
        game.load_room(2, false);
        next();
    } else if (step == 11 && waited > .08f) {
        expect(game.world->remaining_enemies() == 5, "archive chapter loads");
        game.load_room(3, false);
        next();
    } else if (step == 12 && waited > .08f) {
        auto* boss = game.world->get_boss();
        expect(boss && boss->max_health() == 24, "boss configuration loaded");
        boss->hurt(12, boss->get_position() - Vector2(80, 0));
        expect(game.screen == Screen::Dialogue, "boss half-health triggers second-phase story");
        while (game.screen == Screen::Dialogue) {
            game.ui->complete_line();
            game.advance_dialogue();
        }
        game.world->command("stop", Vector2(850, 500));
        expect(game.world->command_count() == 1, "boss command is a world object");
        game.world->strike(Rect2(790, 430, 140, 140), 1);
        next();
    } else if (step == 13 && waited > .15f) {
        expect(game.world->command_count() == 0, "sword interrupts a command before it resolves");
        auto* boss = game.world->get_boss();
        boss->hurt(99, boss->get_position() - Vector2(80, 0));
        next();
    } else if (step == 14 && waited > .85f) {
        expect(game.progress.room == 4, "boss victory transitions to final chapter");
        while (game.screen == Screen::Dialogue) {
            game.ui->complete_line();
            game.advance_dialogue();
        }
        Vector2 at = game.world->get_room().decree;
        game.world->strike(Rect2(at - Vector2(120, 90), Vector2(240, 180)), 1);
        expect(!game.world->decree_intact(), "final decree is severed through the combat system");
        next();
    } else if (step == 15 && waited > 2.9f) {
        expect(game.screen == Screen::Dialogue, "severing the decree reaches epilogue");
        while (game.screen == Screen::Dialogue) {
            game.ui->complete_line();
            game.advance_dialogue();
        }
        expect(game.screen == Screen::Naming, "epilogue grants the player a name");
        game.accept_name(godot::String::utf8("  自由  "));
        expect(game.screen == Screen::Complete && game.hero_name == godot::String::utf8("自由"),
               "Unicode name trims and completes the campaign");
        Ref<ConfigFile> save;
        save.instantiate();
        expect(save->load(game.save_path) == OK && bool(save->get_value("run", "completed", false)),
               "completed run persisted in isolated test save");
        next();
    } else if (step == 16) {
        if (jump_case >= int(sizeof(ROUTES) / sizeof(ROUTES[0]))) {
            game.load_room(0, false);
            next();
            next();
            next();
            return;
        }
        const auto& route = ROUTES[jump_case];
        game.load_room(route.room, false);
        game.world->on_story = nullptr;
        for (auto* e : game.world->get_enemies())
            e->set_process_mode(Node::PROCESS_MODE_DISABLED);
        game.world->get_player()->set_position(route.from);
        game.world->get_player()->set_velocity(Vector2());
        jump_dashed = false;
        next();
    } else if (step == 17 && waited > .12f) {
        expect(game.world->get_player()->is_on_floor(), "route fixture starts on a real platform");
        input->action_press("move_right");
        input->action_press("jump");
        next();
    } else if (step == 18) {
        const auto& route = ROUTES[jump_case];
        auto* p = game.world->get_player();
        if (waited > .3f && !jump_dashed && route.to.x - route.from.x > 240) {
            input->action_press("dash");
            jump_dashed = true;
        }
        if (p->get_position().x >= route.to.x - 4)
            input->action_release("move_right");
        if (waited > .3f && p->is_on_floor() && std::abs(p->get_position().y - route.to.y) < 3 &&
            std::abs(p->get_position().x - route.to.x) < 50) {
            expect(true, "authored gap / rising platform reachable using jump and dash");
            input->action_release("move_right");
            input->action_release("jump");
            input->action_release("dash");
            ++jump_case;
            step = 16;
            frames = 0;
            waited = 0;
        } else if (waited > 2.7f) {
            UtilityFunctions::print("ROUTE ", jump_case, " position=", p->get_position(),
                                    " expected=", route.to);
            expect(false, "authored platform route is reachable");
        }
    } else if (step == 19 && waited > .12f) {
        game.world->get_player()->set_position(Vector2(1450, 610));
        game.world->get_player()->restore();
        for (auto* e : game.world->get_enemies())
            if (e != game.world->get_enemies().back())
                e->set_process_mode(Node::PROCESS_MODE_DISABLED);
        next();
    } else if (step == 20) {
        if (game.world->get_player()->health() < 5) {
            expect(true, "archer projectile aims at and hits a standing player");
            game.world->get_player()->restore();
            next();
        } else if (waited > 3.8f)
            expect(false, "archer projectile reaches player hurtbox");
    } else if (step == 21) {
        float x = game.world->get_player()->get_position().x;
        for (auto& p : game.world->get_projectiles())
            if (!p.friendly && p.p.x - x < 115 && p.p.x - x > 35) {
                input->action_press("attack");
                next();
                break;
            }
        if (waited > 4.8f)
            expect(false, "second projectile available for reflection");
    } else if (step == 22 && waited > .08f) {
        input->action_release("attack");
        bool reflected = false;
        for (auto& p : game.world->get_projectiles())
            if (p.friendly)
                reflected = true;
        expect(reflected, "real slash input reflects an incoming arrow");
        next();
    } else if (step == 23 && waited > 1) {
        expect(!game.world->get_enemies().back()->alive(), "reflected arrow damages its attacker");
        UtilityFunctions::print(
            "INTEGRATION SUCCESS: campaign, platform reachability and projectile reflection verified");
        game.request_quit();
        next();
    }
    if (waited > 8 && step != 15) {
        expect(false, "integration step timed out");
    }
}
} // namespace zhan
