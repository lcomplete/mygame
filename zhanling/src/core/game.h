#pragma once
#include "core/game_data.h"
#include "ui/game_ui.h"
#include <godot_cpp/classes/input_event.hpp>
#include <godot_cpp/classes/node.hpp>
#include <memory>
namespace zhan {
class World;
class Background;
class AudioDirector;
class IntegrationRunner;
class Game : public godot::Node {
    GDCLASS(Game, godot::Node)
    friend class IntegrationRunner;
    GameData data;
    Progress progress;
    World* world = nullptr;
    Background* background = nullptr;
    GameUI* ui = nullptr;
    AudioDirector* audio = nullptr;
    Screen screen = Screen::Title;
    std::vector<DialogueLine> dialogue_lines;
    size_t dialogue_index = 0;
    bool name_after_dialogue = false, has_save = false, smoke_test = false;
    int saved_room = 0, pending_room = -1;
    float transition = 0, chapter_timer = 0, ending_timer = -1, flash = 0, elapsed = 0;
    godot::String save_path = "user://progress.cfg", hero_name;
    godot::String capture_path;
    float capture_at = 2;
    bool captured = false;
    bool exit_after_capture = false;
    float quit_timer = -1;
    void request_quit();
    std::unique_ptr<IntegrationRunner> test;
    void setup_input();
    void set_screen(Screen value);
    void load_room(int index, bool narration = true);
    void begin(bool resume);
    void show_dialogue(const godot::String& id, bool then_name = false);
    void advance_dialogue();
    void action(const godot::String& id);
    void accept_name(const godot::String& value);
    void save();
    void read_save();
    void go_title();
    void schedule_room(int index);
    void take_capture();

  protected:
    static void _bind_methods() {}

  public:
    Game();
    ~Game() override;
    void _ready() override;
    void _notification(int what);
    void _process(double dt) override;
    void _unhandled_input(const godot::Ref<godot::InputEvent>& event) override;
};
} // namespace zhan
