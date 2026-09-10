#pragma once
#include "core/game_data.h"
#include <functional>
#include <godot_cpp/classes/control.hpp>
#include <godot_cpp/classes/line_edit.hpp>
#include <godot_cpp/classes/system_font.hpp>
namespace zhan {
enum class Screen { Title, Playing, Dialogue, Paused, Dead, Naming, Complete, Error };
struct UiModel {
    Screen screen = Screen::Title;
    godot::String chapter = godot::String::utf8("壹 · 雨门"),
                  objective = godot::String::utf8("入城。登楼。处决执笔人。"), hint, error, name;
    int health = 5, max_health = 5, deaths = 0, kills = 0, boss_health = 0, boss_max = 24, foes = 0;
    float dash = 1, chapter_time = 0, flash = 0, fade = 0;
    bool has_save = false, muted = false;
};
class GameUI : public godot::Control {
    GDCLASS(GameUI, godot::Control)
    godot::Ref<godot::SystemFont> font, serif;
    godot::LineEdit* name_input = nullptr;
    DialogueLine line;
    float clock = 0, type_clock = 0;
    void text(const godot::String& s, godot::Vector2 p, int size, godot::Color c, bool title = false);
    void centered(const godot::String& s, float y, int size, godot::Color c, bool title = false);
    void button(const godot::Rect2& r, const godot::String& label, bool primary = false);
    void key(const godot::String& name, godot::Vector2 p, float width = 35);
    void draw_hud();
    void draw_title();
    void draw_dialogue();
    void draw_overlay();
    void _name_submitted(const godot::String& value);

  protected:
    static void _bind_methods();

  public:
    UiModel model;
    std::function<void(const godot::String&)> on_action;
    std::function<void(const godot::String&)> on_name;
    void _ready() override;
    void _process(double dt) override;
    void _draw() override;
    void _gui_input(const godot::Ref<godot::InputEvent>& event) override;
    void dialogue(const DialogueLine& value);
    bool line_complete() const;
    void complete_line() { type_clock = 1000; }
    void focus_name();
    void submit_name();
};
} // namespace zhan
