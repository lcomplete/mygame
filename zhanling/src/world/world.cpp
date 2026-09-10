#include "world/world.h"
#include "actors/actor_visual.h"
#include "actors/enemy.h"
#include "actors/player.h"
#include "ui/typography.h"
#include "world/effects.h"
#include <algorithm>
#include <cmath>
#include <godot_cpp/classes/collision_shape2d.hpp>
#include <godot_cpp/classes/input.hpp>
#include <godot_cpp/classes/rectangle_shape2d.hpp>
#include <godot_cpp/classes/resource_loader.hpp>
#include <godot_cpp/classes/static_body2d.hpp>
using namespace godot;
namespace zhan {
void World::configure(const GameData* d, int index) {
    data = d;
    room_index = index;
    room = data->rooms.at(index);
    seals = room.seals;
}
void World::add_platform(const Rect2& rect) {
    auto* body = memnew(StaticBody2D);
    body->set_collision_layer(1);
    body->set_collision_mask(0);
    body->set_position(rect.get_center());
    auto* shape = memnew(CollisionShape2D);
    Ref<RectangleShape2D> box;
    box.instantiate();
    box->set_size(rect.size);
    shape->set_shape(box);
    if (rect.size.y <= 40) {
        shape->set_one_way_collision(true);
        shape->set_one_way_collision_margin(8);
    }
    body->add_child(shape);
    add_child(body);
}
void World::_ready() {
    if (!data)
        return;
    font = make_font(true);
    auto* loader = ResourceLoader::get_singleton();
    roof = loader->load("res://assets/environment/platform.svg");
    lantern = loader->load("res://assets/environment/lantern.svg");
    banner = loader->load("res://assets/environment/banner.svg");
    crate = loader->load("res://assets/environment/crate.svg");
    scribe = ActorVisual::load_frame("scribe", "idle");
    for (auto& r : room.platforms)
        add_platform(r);
    player = memnew(Player);
    player->configure(data->movement);
    player->set_position(room.spawn);
    player->set_z_index(5);
    player->on_attack = [this](const Rect2& r, int f) { strike(r, f); };
    player->on_sound = [this](const String& s) {
        if (on_sound)
            on_sound(s);
    };
    player->on_died = [this]() {
        if (on_death)
            on_death();
    };
    player->on_hurt = [this]() {
        shake(8, .22f);
        effects->burst(player->get_position() + Vector2(0, -40), Color(.92, .27, .3), 14);
    };
    player->on_trail = [this](Vector2 p, int f) { effects->trail(p, f); };
    player->is_frozen = [this]() { return stop_time > 0; };
    add_child(player);
    effects = memnew(Effects);
    add_child(effects);
    for (auto& s : room.enemies)
        spawn_enemy(s);
    camera = memnew(Camera2D);
    camera->set_position(Vector2(640, 360));
    camera->set_position_smoothing_enabled(false);
    add_child(camera);
    camera->make_current();
}
void World::spawn_enemy(const Spawn& spawn) {
    auto* e = memnew(Enemy);
    e->configure(spawn, data->enemy(spawn.kind), player);
    e->set_z_index(4);
    e->is_frozen = [this]() { return stop_time > 0; };
    e->has_floor = [this](Vector2 p) { return has_floor(p); };
    e->on_melee = [this](const Rect2& r, int damage, Vector2 source) {
        damage_player(r, damage, source);
        effects->slash(source, player->get_position().x < source.x ? -1 : 1, true);
    };
    e->on_shoot = [this](Vector2 p, Vector2 direction) {
        projectiles.push_back({p, direction * data->projectile_speed, false, 5});
    };
    e->on_command = [this](const String& kind, Vector2 p) { command(kind, p); };
    e->on_hit = [this](Vector2 p) {
        stop_time = data->hit_stop;
        shake(4);
        effects->burst(p, Color(1, .77, .48), 18);
        if (on_sound)
            on_sound("hit");
    };
    e->on_died = [this](Enemy* dead) {
        if (on_kill)
            on_kill();
        effects->burst(dead->get_position() + Vector2(0, -48), Color(.86, .24, .33), 25);
        if (dead->boss() && on_boss_defeated)
            on_boss_defeated();
    };
    e->on_phase = [this]() {
        shake(12, .5);
        if (on_phase)
            on_phase();
    };
    enemies.push_back(e);
    add_child(e);
}
bool World::has_floor(Vector2 p) const {
    for (auto& r : room.platforms)
        if (r.has_point(p))
            return true;
    return false;
}
int World::remaining_enemies() const {
    int n = 0;
    for (auto* e : enemies)
        if (e->alive())
            ++n;
    return n;
}
bool World::clear() const {
    return remaining_enemies() == 0 && seals.empty();
}
Enemy* World::get_boss() const {
    for (auto* e : enemies)
        if (e->boss())
            return e;
    return nullptr;
}
float World::camera_left() const {
    return camera ? camera->get_position().x - 640 : 0;
}
bool World::at_exit() const {
    return player && player->get_position().distance_to(room.exit + Vector2(0, 90)) < 145;
}
String World::hint() const {
    if (!player)
        return "";
    if (at_exit())
        return clear() ? godot::String::utf8("[ E ] 前往下一章")
                       : godot::String::utf8("斩断封印，清除守卫后通行。");
    String result = "";
    for (auto& h : room.hints)
        if (player->get_position().x >= h.x - 180)
            result = h.text;
    return result;
}
void World::shake(float strength, float duration) {
    shake_power = std::max(shake_power, strength);
    shake_time = duration;
}
void World::damage_player(const Rect2& rect, int damage, Vector2 source) {
    if (player->hurtbox().intersects(rect))
        player->hurt(damage, source);
}
void World::command(const String& kind, Vector2 at) {
    at.x = std::clamp(at.x, 180.f, room.width - 180);
    at.y = std::clamp(at.y, 200.f, 530.f);
    glyphs.push_back({at, kind, data->command_windup, data->command_windup, true});
    if (on_sound)
        on_sound("glyph");
}
void World::strike(const Rect2& rect, int facing) {
    effects->slash(player->get_position(), facing);
    for (auto* e : enemies)
        if (e->alive() && e->hurtbox().intersects(rect))
            e->hurt(data->player_damage, player->get_position());
    for (auto& p : projectiles)
        if (!p.friendly && rect.grow(15).has_point(p.p)) {
            p.friendly = true;
            p.velocity = -p.velocity * 1.65f;
            effects->burst(p.p, Color(.6, 1, .88), 12);
            shake(3);
        }
    seals.erase(std::remove_if(seals.begin(), seals.end(),
                               [&](Vector2 p) {
                                   if (!Rect2(p - Vector2(31, 47), Vector2(62, 94)).intersects(rect))
                                       return false;
                                   effects->burst(p, Color(1, .48, .36), 32);
                                   shake(9, .25);
                                   if (on_sound)
                                       on_sound("glyph");
                                   return true;
                               }),
                seals.end());
    for (auto& g : glyphs)
        if (g.live && Rect2(g.p - Vector2(38, 42), Vector2(76, 84)).intersects(rect)) {
            g.live = false;
            effects->burst(g.p, Color(.7, 1, .8), 25);
            shake(5);
        }
    if (room.decree.x >= 0 && decree_live &&
        Rect2(room.decree - Vector2(115, 50), Vector2(230, 100)).intersects(rect)) {
        decree_live = false;
        effects->burst(room.decree, Color(1, .73, .55), 100);
        shake(22, .8f);
        if (on_sound)
            on_sound("victory");
        if (on_decree_cut)
            on_decree_cut();
    }
}
void World::_process(double delta) {
    float dt = float(delta);
    clock += dt;
    tick(stop_time, dt);
    tick(shake_time, dt);
    if (camera && player) {
        float desired = std::clamp(player->get_position().x + 100, 640.f, room.width - 640);
        Vector2 position = camera->get_position();
        position.x = approach(position.x, desired, dt * 850);
        camera->set_position(position);
        camera->set_offset(shake_time > 0 ? Vector2(std::sin(clock * 131) * shake_power,
                                                    std::cos(clock * 99) * shake_power) *
                                                std::min(1.f, shake_time * 5)
                                          : Vector2());
        if (shake_time <= 0)
            shake_power = 0;
    }
    queue_redraw();
}
void World::_physics_process(double delta) {
    if (!player || stop_time > 0)
        return;
    float dt = float(delta);
    for (auto& p : projectiles) {
        p.life -= dt;
        p.p += p.velocity * dt;
        if (has_floor(p.p)) {
            p.life = 0;
            effects->burst(p.p, Color(.5, .65, .65), 4);
            continue;
        }
        if (p.friendly) {
            for (auto* e : enemies)
                if (e->alive() && e->hurtbox().grow(8).has_point(p.p)) {
                    e->hurt(3, p.p - p.velocity);
                    p.life = 0;
                    break;
                }
        } else if (player->hurtbox().grow(3).has_point(p.p) && player->hurt(1, p.p - p.velocity))
            p.life = 0;
    }
    projectiles.erase(
        std::remove_if(projectiles.begin(), projectiles.end(), [](auto& p) { return p.life <= 0; }),
        projectiles.end());
    for (auto& g : glyphs)
        if (g.live) {
            g.time -= dt;
            if (g.time <= 0) {
                g.live = false;
                effects->burst(g.p, Color(.9, .22, .3), 30);
                shake(5);
                if (g.kind == "kill") {
                    for (int sign : {-1, 1}) {
                        Spawn s;
                        s.kind = "soldier";
                        s.at = Vector2(std::clamp(g.p.x + sign * 180, 200.f, room.width - 200), 580);
                        s.left = 160;
                        s.right = room.width - 160;
                        spawn_enemy(s);
                    }
                } else
                    damage_player(Rect2(g.p.x - 100, 100, 200, 520), 1, g.p);
            }
        }
    glyphs.erase(std::remove_if(glyphs.begin(), glyphs.end(), [](auto& g) { return !g.live; }), glyphs.end());
    if (!story_triggered && !room.story.is_empty() && player->get_position().x >= room.story_x) {
        story_triggered = true;
        if (on_story)
            on_story(room.story);
    }
    if (!exiting && room.decree.x < 0 && get_boss() == nullptr && clear() && at_exit() &&
        Input::get_singleton()->is_action_just_pressed("interact")) {
        exiting = true;
        if (on_exit)
            on_exit();
    }
    Vector2 p = player->get_position();
    if (p.x < 25 || p.x > room.width - 25) {
        p.x = std::clamp(p.x, 25.f, room.width - 25);
        player->set_position(p);
    }
}
void World::_draw() {
    if (roof.is_null())
        return;
    // Rooftops and inset supports keep all solid surfaces visually consistent.
    for (auto& r : room.platforms) {
        float face = std::min(r.size.y, 96.f);
        for (float x = r.position.x; x < r.get_end().x; x += 256) {
            float w = std::min(256.f, r.get_end().x - x);
            draw_texture_rect_region(roof, Rect2(x, r.position.y, w, face), Rect2(0, 0, w, face));
        }
        if (r.size.y > 96)
            draw_rect(Rect2(r.position.x, r.position.y + 96, r.size.x, r.size.y - 96),
                      Color(.026, .056, .081));
        if (r.size.y < 40) {
            draw_line(r.position + Vector2(12, r.size.y), r.position + Vector2(26, r.size.y + 30),
                      Color(.12, .22, .27), 4);
            draw_line(r.get_end() - Vector2(12, 0), r.get_end() + Vector2(-28, 30), Color(.12, .22, .27), 4);
        }
        draw_line(r.position + Vector2(4, -1), Vector2(r.get_end().x - 4, r.position.y - 1),
                  Color(.4, .67, .67, .6), 1, true);
    }
    // Rain reflections and ripples sit on the ground, independent from colliders.
    for (int i = 0; i < 35; ++i) {
        float x = i * 79 + 18;
        if (x > room.width)
            break;
        if (has_floor(Vector2(x, 615))) {
            float phase = std::fmod(clock * .75f + i * .19f, 1.f);
            draw_set_transform(Vector2(x, 615), 0, Vector2(1, .16));
            draw_arc(Vector2(), 4 + phase * 18, 0, 6.283, 18, Color(.46, .67, .69, (1 - phase) * .22f), 1,
                     true);
        }
    }
    draw_set_transform(Vector2(), 0, Vector2(1, 1));
    for (auto p : room.lanterns) {
        draw_line(Vector2(p.x, -40), p, Color(.04, .1, .14), 2);
        for (int j = 4; j > 0; --j)
            draw_circle(p + Vector2(0, 45), 16 + j * 12, Color(.95, .45, .26, .012f));
        draw_texture_rect(lantern, Rect2(p - Vector2(25, 0), Vector2(50, 82)), false, Color(1, 1, 1, .93));
    }
    if (room.decree.x < 0) {
        for (float x = 350; x < room.width; x += 690)
            draw_texture_rect(banner, Rect2(x, 40, 67, 154), false, Color(.8, .8, .8, .64));
    }
    if (room.story == "merchant") {
        draw_texture_rect(crate, Rect2(760, 560, 50, 50), false);
        Rect2 scribe_rect = ActorVisual::frame_rect(scribe);
        scribe_rect.position += Vector2(881, 610);
        ActorVisual::draw_frame(this, scribe, scribe_rect);
    }
    if (get_boss() != nullptr) {
        Rect2 scribe_rect = ActorVisual::frame_rect(scribe, 100);
        scribe_rect.position += Vector2(810, 612);
        ActorVisual::draw_frame(this, scribe, scribe_rect, Color(.55, .46, .5, .5));
    }
    // The exit arch is accessible only after the written seal and its guards are gone.
    if (room.decree.x < 0 && get_boss() == nullptr) {
        Vector2 p = room.exit;
        draw_rect(Rect2(p.x - 37, p.y - 24, 92, 135), Color(.055, .12, .16));
        draw_rect(Rect2(p.x - 32, p.y - 20, 82, 130), Color(.32, .48, .48), false, 3);
        draw_rect(Rect2(p.x - 40, p.y - 28, 99, 9), Color(.54, .4, .31));
        Color c = clear() ? Color(.59, .87, .73) : Color(.71, .31, .33);
        draw_string(font, p + Vector2(-14, 15),
                    clear() ? godot::String::utf8("行") : godot::String::utf8("禁"),
                    HORIZONTAL_ALIGNMENT_LEFT, -1, 29, c);
        if (clear())
            draw_string(font, p + Vector2(-3, -47), "E", HORIZONTAL_ALIGNMENT_LEFT, -1, 18,
                        Color(.79, .9, .8));
    }
    for (auto p : seals) {
        float glow = .8f + .2f * std::sin(clock * 3);
        draw_line(p + Vector2(0, -800), p, Color(.67, .2, .25, .6), 2);
        draw_rect(Rect2(p - Vector2(29, 45), Vector2(58, 90)), Color(.66, .25, .28, .9));
        draw_rect(Rect2(p - Vector2(24, 40), Vector2(48, 80)), Color(1, .64, .46, glow), false, 1);
        draw_string(font, p + Vector2(-20, 13), godot::String::utf8("封"), HORIZONTAL_ALIGNMENT_LEFT, -1, 41,
                    Color(1, .84, .59));
    }
    for (auto& p : projectiles) {
        Color c = p.friendly ? Color(.6, 1, .84) : Color(1, .59, .44);
        Vector2 d = p.velocity.normalized();
        draw_line(p.p - d * 29, p.p, c, 2, true);
        draw_line(p.p, p.p - d.rotated(.5) * 9, c, 2, true);
        draw_line(p.p, p.p - d.rotated(-.5) * 9, c, 2, true);
    }
    for (auto& g : glyphs) {
        float progress = 1 - g.time / g.total;
        draw_circle(g.p, 52, Color(.72, .15, .25, .12));
        draw_arc(g.p, 48, -1.57f, -1.57f + progress * 6.283f, 40, Color(1, .44, .38), 2, true);
        draw_string(font, g.p + Vector2(-28, 21),
                    g.kind == "kill" ? godot::String::utf8("杀") : godot::String::utf8("止"),
                    HORIZONTAL_ALIGNMENT_LEFT, -1, 56, Color(1, .68, .48));
        draw_rect(Rect2(g.p.x - 100, 604, 200, 5), Color(.95, .28, .3, .35 + progress * .4));
    }
    if (room.decree.x >= 0 && decree_live) {
        Vector2 p = room.decree;
        draw_line(p - Vector2(0, 50), Vector2(p.x, -500), Color(.94, .37, .4, .75), 3);
        if (player)
            draw_line(p, player->get_position() + Vector2(20, -60), Color(.84, .19, .3, .48), 2, true);
        draw_rect(Rect2(p - Vector2(134, 69), Vector2(268, 138)), Color(.15, .065, .105, .98));
        draw_rect(Rect2(p - Vector2(127, 62), Vector2(254, 124)), Color(.76, .33, .34), false, 2);
        draw_rect(Rect2(p - Vector2(122, 57), Vector2(244, 114)), Color(.46, .23, .24), false, 1);
        draw_string(font, p + Vector2(-49, 31), godot::String::utf8("跪"), HORIZONTAL_ALIGNMENT_LEFT, -1, 100,
                    Color(1, .7, .51));
        draw_string(font, p + Vector2(-47, -89), godot::String::utf8("最后一道命令"),
                    HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(.94, .62, .5));
    }
}
} // namespace zhan
