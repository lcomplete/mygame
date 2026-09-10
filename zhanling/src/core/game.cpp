#include "core/game.h"
#include "../../tests/integration_runner.h"
#include "actors/actor_visual.h"
#include "actors/enemy.h"
#include "actors/player.h"
#include "audio/audio_director.h"
#include "world/background.h"
#include "world/world.h"
#include <algorithm>
#include <godot_cpp/classes/canvas_layer.hpp>
#include <godot_cpp/classes/config_file.hpp>
#include <godot_cpp/classes/display_server.hpp>
#include <godot_cpp/classes/engine.hpp>
#include <godot_cpp/classes/image.hpp>
#include <godot_cpp/classes/input.hpp>
#include <godot_cpp/classes/input_event_joypad_button.hpp>
#include <godot_cpp/classes/input_event_joypad_motion.hpp>
#include <godot_cpp/classes/input_event_key.hpp>
#include <godot_cpp/classes/input_event_mouse_button.hpp>
#include <godot_cpp/classes/input_map.hpp>
#include <godot_cpp/classes/os.hpp>
#include <godot_cpp/classes/scene_tree.hpp>
#include <godot_cpp/classes/viewport.hpp>
#include <godot_cpp/classes/viewport_texture.hpp>
#include <godot_cpp/variant/utility_functions.hpp>
using namespace godot;
namespace zhan {
Game::Game() = default;
Game::~Game() = default;
static void release_controls() {
    for (const char* s : {"move_left", "move_right", "jump", "attack", "dash", "interact"})
        Input::get_singleton()->action_release(s);
}
void Game::setup_input() {
    auto* map = InputMap::get_singleton();
    auto bind = [&](const char* name, std::initializer_list<Key> keys) {
        if (!map->has_action(name))
            map->add_action(name, .22);
        for (Key key : keys) {
            Ref<InputEventKey> e;
            e.instantiate();
            e->set_physical_keycode(key);
            map->action_add_event(name, e);
        }
    };
    bind("move_left", {KEY_A, KEY_LEFT});
    bind("move_right", {KEY_D, KEY_RIGHT});
    bind("jump", {KEY_SPACE, KEY_W, KEY_UP});
    bind("attack", {KEY_J});
    bind("dash", {KEY_K, KEY_SHIFT});
    bind("interact", {KEY_E});
    // Gamepad support uses the same action layer as keyboard and integration tests.
    for (auto pair : std::vector<std::pair<const char*, JoyButton>>{{"jump", JOY_BUTTON_A},
                                                                    {"attack", JOY_BUTTON_X},
                                                                    {"dash", JOY_BUTTON_B},
                                                                    {"interact", JOY_BUTTON_Y},
                                                                    {"move_left", JOY_BUTTON_DPAD_LEFT},
                                                                    {"move_right", JOY_BUTTON_DPAD_RIGHT}}) {
        Ref<InputEventJoypadButton> e;
        e.instantiate();
        e->set_button_index(pair.second);
        map->action_add_event(pair.first, e);
    }
    for (auto pair : std::vector<std::pair<const char*, float>>{{"move_left", -1.f}, {"move_right", 1.f}}) {
        Ref<InputEventJoypadMotion> e;
        e.instantiate();
        e->set_axis(JOY_AXIS_LEFT_X);
        e->set_axis_value(pair.second);
        map->action_add_event(pair.first, e);
    }
}
void Game::_ready() {
    if (Engine::get_singleton()->is_editor_hint())
        return;
    set_name("Zhanling");
    get_tree()->set_auto_accept_quit(false);
    setup_input();
    int preview_room = -1;
    for (const String& arg : OS::get_singleton()->get_cmdline_user_args()) {
        if (arg == "--exit-after-capture")
            exit_after_capture = true;
        if (arg == "--smoke-test")
            smoke_test = true;
        if (arg.begins_with("--capture="))
            capture_path = arg.substr(10);
        if (arg.begins_with("--room="))
            preview_room = arg.substr(7).to_int();
    }
    if (smoke_test)
        save_path = "user://integration_progress.cfg";
    else if (preview_room >= 0)
        save_path = "user://preview_progress.cfg";
    auto* back_layer = memnew(CanvasLayer);
    back_layer->set_layer(-10);
    add_child(back_layer);
    background = memnew(Background);
    back_layer->add_child(background);
    auto* ui_layer = memnew(CanvasLayer);
    ui_layer->set_layer(10);
    add_child(ui_layer);
    ui = memnew(GameUI);
    ui_layer->add_child(ui);
    ui->on_action = [this](const String& id) { action(id); };
    ui->on_name = [this](const String& value) { accept_name(value); };
    if (!data.load()) {
        ui->model.error = data.error;
        set_screen(Screen::Error);
        UtilityFunctions::push_error(data.error);
        if (smoke_test)
            get_tree()->quit(1);
        return;
    }
    audio = memnew(AudioDirector);
    audio->configure(data.music_db, data.effects_db);
    add_child(audio);
    read_save();
    set_screen(Screen::Title);
    if (preview_room >= 0) {
        progress = {};
        load_room(std::clamp(preview_room, 0, int(data.rooms.size()) - 1), false);
    }
    if (smoke_test) {
        audio->set_muted(true);
        test = std::make_unique<IntegrationRunner>(*this);
    }
}
void Game::set_screen(Screen value) {
    screen = value;
    if (ui)
        ui->model.screen = value;
    if (world)
        world->set_process_mode(value == Screen::Playing ? Node::PROCESS_MODE_INHERIT
                                                         : Node::PROCESS_MODE_DISABLED);
}
void Game::read_save() {
    Ref<ConfigFile> config;
    config.instantiate();
    if (config->load(save_path) == OK) {
        progress.room = int(config->get_value("run", "room", 0));
        if (config->has_section_key("run", "room_id")) {
            int found = data.room_index(config->get_value("run", "room_id", ""));
            progress.room = found >= 0 ? found : 0;
        }
        progress.deaths = int(config->get_value("run", "deaths", 0));
        progress.kills = int(config->get_value("run", "kills", 0));
        progress.completed = bool(config->get_value("run", "completed", false));
        progress.sanitize(int(data.rooms.size()));
        saved_room = progress.room;
        has_save = config->has_section_key("run", "room") && !progress.completed;
        hero_name = config->get_value("run", "name", "");
        audio->set_muted(bool(config->get_value("settings", "muted", false)));
    }
}
void Game::save() {
    Ref<ConfigFile> config;
    config.instantiate();
    config->set_value("run", "room", progress.room);
    config->set_value("run", "room_id", data.rooms.at(progress.room).id);
    config->set_value("run", "deaths", progress.deaths);
    config->set_value("run", "kills", progress.kills);
    config->set_value("run", "completed", progress.completed);
    config->set_value("run", "name", hero_name);
    config->set_value("settings", "muted", audio && audio->is_muted());
    if (config->save(save_path) != OK)
        UtilityFunctions::push_warning(godot::String::utf8("章节存档写入失败: ") + save_path);
    saved_room = progress.room;
    has_save = !progress.completed;
}
void Game::begin(bool resume) {
    release_controls();
    if (!resume) {
        progress = {};
        hero_name = "";
    } else {
        read_save();
        progress.room = saved_room;
    }
    load_room(progress.room, true);
}
void Game::load_room(int index, bool narration) {
    release_controls();
    pending_room = -1;
    transition = 0;
    ending_timer = -1;
    if (world) {
        world->set_process_mode(Node::PROCESS_MODE_DISABLED);
        world->hide();
        world->queue_free();
        world = nullptr;
    }
    progress.room = index;
    progress.completed = false;
    save();
    world = memnew(World);
    world->configure(&data, index);
    world->on_sound = [this](const String& s) { audio->play(s); };
    world->on_kill = [this]() { ++progress.kills; };
    world->on_exit = [this]() {
        int next = data.room_index(world->get_room().next);
        if (next >= 0)
            schedule_room(next);
    };
    world->on_death = [this]() {
        if (pending_room >= 0 || ending_timer > 0)
            return;
        ++progress.deaths;
        save();
        set_screen(Screen::Dead);
    };
    world->on_story = [this](const String& id) { show_dialogue(id); };
    world->on_boss_defeated = [this]() {
        audio->play("bell");
        int next = data.room_index(world->get_room().next);
        if (next >= 0)
            schedule_room(next);
    };
    world->on_phase = [this]() { show_dialogue("boss_phase"); };
    world->on_decree_cut = [this]() {
        ending_timer = 2.6f;
        flash = .85f;
        world->set_process_mode(Node::PROCESS_MODE_DISABLED);
    };
    add_child(world);
    background->set_title(false);
    background->set_chapter(index);
    background->set_daylight(0);
    chapter_timer = 4;
    set_screen(Screen::Playing);
    if (narration && !data.rooms[index].intro.is_empty())
        show_dialogue(data.rooms[index].intro);
}
void Game::show_dialogue(const String& id, bool then_name) {
    dialogue_lines = data.dialogue(id);
    if (dialogue_lines.empty())
        return;
    name_after_dialogue = then_name;
    dialogue_index = 0;
    ui->dialogue(dialogue_lines[0]);
    set_screen(Screen::Dialogue);
}
void Game::advance_dialogue() {
    if (screen != Screen::Dialogue)
        return;
    if (!ui->line_complete()) {
        ui->complete_line();
        return;
    }
    ++dialogue_index;
    if (dialogue_index < dialogue_lines.size()) {
        const auto& line = dialogue_lines[dialogue_index];
        ui->dialogue(line);
        if (world && world->get_player()->get_visual()) {
            bool kneel = line.text.contains(godot::String::utf8("——跪")) ||
                         line.text.contains(godot::String::utf8("我的身体"));
            world->get_player()->get_visual()->set_position(Vector2(0, kneel ? 24 : 0));
        }
    } else {
        if (world && world->get_player()->get_visual())
            world->get_player()->get_visual()->set_position(Vector2());
        if (name_after_dialogue) {
            set_screen(Screen::Naming);
            ui->focus_name();
        } else
            set_screen(Screen::Playing);
        release_controls();
    }
}
void Game::schedule_room(int index) {
    pending_room = index;
    transition = .65f;
    if (world)
        world->set_process_mode(Node::PROCESS_MODE_DISABLED);
}
void Game::go_title() {
    release_controls();
    pending_room = -1;
    ending_timer = -1;
    transition = 0;
    if (world) {
        world->queue_free();
        world = nullptr;
    }
    background->set_title(true);
    background->set_daylight(0);
    background->set_camera_x(0);
    background->set_chapter(0);
    set_screen(Screen::Title);
    read_save();
}
void Game::action(const String& id) {
    if (id == "start")
        begin(false);
    else if (id == "continue")
        begin(true);
    else if (id == "resume" && screen == Screen::Paused)
        set_screen(Screen::Playing);
    else if (id == "restart" && world)
        load_room(progress.room, true);
    else if (id == "title")
        go_title();
    else if (id == "advance")
        advance_dialogue();
    else if (id == "quit")
        request_quit();
}
void Game::accept_name(const String& value) {
    if (screen != Screen::Naming)
        return;
    String name = value.strip_edges();
    if (name.is_empty()) {
        ui->model.error = godot::String::utf8("请写下你自己的名字。");
        return;
    }
    hero_name = name.substr(0, 12);
    progress.completed = true;
    save();
    ui->model.name = hero_name;
    ui->model.error = "";
    audio->play("bell");
    set_screen(Screen::Complete);
}
void Game::take_capture() {
    if (capture_path.is_empty() || captured)
        return;
    Ref<ViewportTexture> texture = get_viewport()->get_texture();
    if (texture.is_null())
        return;
    Ref<Image> image = texture->get_image();
    if (image.is_null() || image->is_empty())
        return;
    Error error = image->save_png(capture_path);
    UtilityFunctions::print("CAPTURE: ", capture_path, " result=", int(error));
    captured = true;
    if (exit_after_capture)
        request_quit();
}
void Game::request_quit() {
    if (quit_timer >= 0)
        return;
    if (audio)
        audio->set_muted(true);
    if (world)
        world->set_process_mode(Node::PROCESS_MODE_DISABLED);
    quit_timer = .18f;
}
void Game::_notification(int what) {
    if (what == NOTIFICATION_WM_CLOSE_REQUEST && !Engine::get_singleton()->is_editor_hint())
        request_quit();
}
void Game::_process(double delta) {
    if (Engine::get_singleton()->is_editor_hint() || !ui)
        return;
    float dt = float(delta);
    if (quit_timer >= 0) {
        quit_timer -= dt;
        if (quit_timer <= 0)
            get_tree()->quit();
        return;
    }
    elapsed += dt;
    tick(flash, dt);
    tick(chapter_timer, dt);
    if (pending_room >= 0) {
        tick(transition, dt);
        if (transition <= 0)
            load_room(pending_room, true);
    }
    if (ending_timer > 0) {
        ending_timer -= dt;
        background->set_daylight(std::clamp((2.6f - ending_timer) / 2.2f, 0.f, 1.f));
        if (ending_timer <= 0) {
            ending_timer = -1;
            show_dialogue("ending", true);
        }
    }
    auto& m = ui->model;
    m.has_save = has_save;
    m.muted = audio && audio->is_muted();
    m.deaths = progress.deaths;
    m.kills = progress.kills;
    m.flash = flash;
    m.fade = pending_room >= 0 ? 1 - transition / .65f : 0;
    m.chapter_time = chapter_timer;
    if (world) {
        Player* p = world->get_player();
        m.health = p->health();
        m.max_health = p->max_health();
        m.dash = p->dash_ready();
        m.chapter = world->get_room().title;
        m.objective = world->get_room().objective;
        m.hint = world->hint();
        m.foes = world->remaining_enemies();
        auto* boss = world->get_boss();
        m.boss_health = boss ? boss->health() : 0;
        m.boss_max = boss ? boss->max_health() : 24;
        background->set_camera_x(world->camera_left());
    }
    if (!captured && elapsed > capture_at)
        take_capture();
    if (test)
        test->update(dt);
}
void Game::_unhandled_input(const Ref<InputEvent>& event) {
    Ref<InputEventKey> key = event;
    if (key.is_null() || !key->is_pressed() || key->is_echo())
        return;
    Key code = key->get_keycode();
    if (code == KEY_F11) {
        auto* d = DisplayServer::get_singleton();
        d->window_set_mode(d->window_get_mode() == DisplayServer::WINDOW_MODE_FULLSCREEN
                               ? DisplayServer::WINDOW_MODE_WINDOWED
                               : DisplayServer::WINDOW_MODE_FULLSCREEN);
        return;
    }
    if (code == KEY_M && screen != Screen::Naming && audio) {
        audio->set_muted(!audio->is_muted());
        if (world || has_save)
            save();
        return;
    }
    if (code == KEY_ESCAPE) {
        if (screen == Screen::Playing && pending_room < 0 && ending_timer < 0)
            set_screen(Screen::Paused);
        else if (screen == Screen::Paused)
            set_screen(Screen::Playing);
        return;
    }
    if (screen == Screen::Title && code == KEY_ENTER)
        begin(false);
    else if (screen == Screen::Dialogue && (code == KEY_ENTER || code == KEY_E))
        advance_dialogue();
    else if (screen == Screen::Dead && (code == KEY_ENTER || code == KEY_R))
        action("restart");
    else if (screen == Screen::Paused && code == KEY_R)
        action("restart");
    else if (screen == Screen::Complete && code == KEY_ENTER)
        go_title();
}
} // namespace zhan
