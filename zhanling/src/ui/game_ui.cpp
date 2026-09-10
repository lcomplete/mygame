#include "ui/game_ui.h"
#include "ui/typography.h"
#include <cmath>
#include <godot_cpp/classes/input_event_mouse_button.hpp>
#include <godot_cpp/classes/style_box_flat.hpp>
#include <godot_cpp/core/class_db.hpp>
using namespace godot;
namespace zhan {
static const Color CREAM(.88, .88, .78), MUTED(.49, .64, .65), RED(.79, .30, .32), GOLD(.77, .56, .4),
    TEAL(.49, .85, .79);
void GameUI::_bind_methods() {
    ClassDB::bind_method(D_METHOD("_name_submitted", "value"), &GameUI::_name_submitted);
}
void GameUI::_ready() {
    set_anchors_and_offsets_preset(Control::PRESET_FULL_RECT);
    set_mouse_filter(Control::MOUSE_FILTER_STOP);
    font = make_font();
    serif = make_font(true);
    name_input = memnew(LineEdit);
    name_input->set_position(Vector2(442, 363));
    name_input->set_size(Vector2(396, 60));
    name_input->set_max_length(12);
    name_input->set_placeholder(godot::String::utf8("给自己起一个名字"));
    name_input->set_horizontal_alignment(HORIZONTAL_ALIGNMENT_CENTER);
    name_input->add_theme_font_override("font", font);
    name_input->add_theme_font_size_override("font_size", 26);
    name_input->add_theme_color_override("font_color", CREAM);
    name_input->add_theme_color_override("caret_color", TEAL);
    Ref<StyleBoxFlat> style;
    style.instantiate();
    style->set_bg_color(Color(.06, .12, .15));
    style->set_border_width_all(1);
    style->set_border_color(GOLD);
    style->set_content_margin(SIDE_LEFT, 15);
    style->set_content_margin(SIDE_RIGHT, 15);
    name_input->add_theme_stylebox_override("normal", style);
    name_input->add_theme_stylebox_override("focus", style);
    name_input->connect("text_submitted", Callable(this, "_name_submitted"));
    add_child(name_input);
    name_input->hide();
}
void GameUI::_name_submitted(const String& value) {
    if (on_name)
        on_name(value);
}
void GameUI::submit_name() {
    if (name_input && on_name)
        on_name(name_input->get_text());
}
void GameUI::focus_name() {
    name_input->show();
    name_input->set_text("");
    name_input->grab_focus();
}
void GameUI::dialogue(const DialogueLine& value) {
    line = value;
    type_clock = 0;
}
bool GameUI::line_complete() const {
    return type_clock * 32 >= line.text.length();
}
void GameUI::_process(double dt) {
    clock += dt;
    type_clock += dt;
    if (name_input)
        name_input->set_visible(model.screen == Screen::Naming);
    queue_redraw();
}
void GameUI::text(const String& s, Vector2 p, int size, Color c, bool title) {
    draw_string(title ? serif : font, p, s, HORIZONTAL_ALIGNMENT_LEFT, -1, size, c);
}
void GameUI::centered(const String& s, float y, int size, Color c, bool title) {
    draw_string(title ? serif : font, Vector2(0, y), s, HORIZONTAL_ALIGNMENT_CENTER, 1280, size, c);
}
void GameUI::button(const Rect2& r, const String& label, bool primary) {
    bool hover = r.has_point(get_local_mouse_position());
    draw_rect(r, primary ? Color(.46, .14, .19, hover ? .97 : .88) : Color(.05, .11, .15, .9));
    draw_rect(r, hover ? CREAM : primary ? RED : Color(.3, .44, .47), false, 1);
    draw_rect(Rect2(r.position, Vector2(3, r.size.y)), primary ? RED : TEAL);
    text(label, r.position + Vector2(24, r.size.y / 2 + 7), 21, CREAM);
    text(godot::String::utf8("›"), r.position + Vector2(r.size.x - 31, r.size.y / 2 + 9), 26,
         primary ? Color(1, .63, .46) : TEAL);
}
void GameUI::key(const String& name, Vector2 p, float width) {
    draw_rect(Rect2(p, Vector2(width, 27)), Color(.07, .13, .17, .9));
    draw_rect(Rect2(p, Vector2(width, 27)), Color(.33, .46, .49), false, 1);
    draw_string(font, p + Vector2(0, 19), name, HORIZONTAL_ALIGNMENT_CENTER, width, 13, CREAM);
}
void GameUI::draw_title() {
    // Quiet left-hand scrim gives the title a clean, cinematic hierarchy.
    for (int i = 0; i < 45; ++i)
        draw_rect(Rect2(i * 16, 0, 16, 720), Color(.012, .029, .044, .84f * (1 - i / 50.f)));
    draw_line(Vector2(86, 111), Vector2(142, 111), GOLD, 1, true);
    text(godot::String::utf8("一夜 · 一刀 · 一个自己的名字"), Vector2(157, 117), 16, GOLD);
    text(godot::String::utf8("斩令"), Vector2(80, 298), 152, CREAM, true);
    draw_rect(Rect2(424, 178, 35, 84), Color(.56, .18, .23), false, 1);
    text(godot::String::utf8("无"), Vector2(431, 209), 22, Color(.87, .52, .42), true);
    text(godot::String::utf8("令"), Vector2(431, 241), 22, Color(.87, .52, .42), true);
    text("S E V E R   T H E   D E C R E E", Vector2(92, 341), 19, TEAL);
    text(godot::String::utf8("你从未违抗过命令。"), Vector2(91, 398), 22, CREAM, true);
    text(godot::String::utf8("今夜，斩断最后一道。"), Vector2(91, 431), 22, CREAM, true);
    button(Rect2(90, 487, 278, 59), godot::String::utf8("踏入雨夜  /  开始"), true);
    if (model.has_save)
        button(Rect2(391, 487, 222, 59), godot::String::utf8("继续上一章"));
    text(godot::String::utf8("ENTER 开始"), Vector2(92, 573), 13, MUTED);
    draw_line(Vector2(90, 613), Vector2(615, 613), Color(.25, .4, .43, .7), 1, true);
    key("A D", Vector2(90, 640), 48);
    text(godot::String::utf8("移动"), Vector2(149, 660), 14, MUTED);
    key("SPACE", Vector2(211, 640), 63);
    text(godot::String::utf8("跳跃"), Vector2(285, 660), 14, MUTED);
    key("J", Vector2(349, 640));
    text(godot::String::utf8("斩击"), Vector2(396, 660), 14, MUTED);
    key("SHIFT", Vector2(460, 640), 62);
    text(godot::String::utf8("突进"), Vector2(533, 660), 14, MUTED);
    text(godot::String::utf8("东方奇谭 · 横版动作短篇"), Vector2(975, 667), 14, Color(.54, .69, .67));
    text(model.muted ? godot::String::utf8("M  声音已关闭") : godot::String::utf8("M  声音开启"),
         Vector2(1092, 38), 13, MUTED);
    draw_line(Vector2(1180, 75), Vector2(1210, 75), GOLD, 1);
    draw_line(Vector2(1210, 75), Vector2(1210, 106), GOLD, 1);
}
void GameUI::draw_hud() {
    draw_rect(Rect2(0, 0, 1280, 111), Color(.017, .04, .063, .66));
    text(godot::String::utf8("影 十 七"), Vector2(37, 35), 16, CREAM, true);
    for (int i = 0; i < model.max_health; ++i) {
        float x = 47 + i * 26, y = 58;
        PackedVector2Array points;
        points.push_back(Vector2(x, y - 7));
        points.push_back(Vector2(x + 6, y));
        points.push_back(Vector2(x, y + 7));
        points.push_back(Vector2(x - 6, y));
        draw_colored_polygon(points, i < model.health ? Color(.91, .47, .4) : Color(.21, .27, .3));
    }
    draw_rect(Rect2(39, 79, 124, 3), Color(.2, .31, .34));
    draw_rect(Rect2(39, 79, 124 * std::clamp(model.dash, 0.f, 1.f), 3), TEAL);
    text(godot::String::utf8("刀在手。"), Vector2(38, 102), 11, MUTED);
    // The objective scroll is deliberately also a physical object in the finale.
    draw_rect(Rect2(409, 20, 478, 66), Color(.16, .067, .1, .93));
    draw_rect(Rect2(409, 20, 478, 66), Color(.47, .24, .25), false, 1);
    draw_line(Vector2(414, 14), Vector2(414, 92), GOLD, 3);
    draw_line(Vector2(882, 14), Vector2(882, 92), GOLD, 3);
    text(godot::String::utf8("朱 令"), Vector2(431, 45), 12, Color(.88, .46, .39));
    draw_string(serif, Vector2(492, 65), model.objective, HORIZONTAL_ALIGNMENT_LEFT, 375, 20, CREAM);
    draw_line(Vector2(876, 86), Vector2(886, 107), Color(.66, .2, .29, .75), 1);
    draw_string(font, Vector2(946, 37), model.chapter, HORIZONTAL_ALIGNMENT_RIGHT, 293, 20, CREAM);
    draw_string(font, Vector2(1010, 66),
                godot::String::utf8("余敌 ") + String::num_int64(model.foes) +
                    godot::String::utf8("   /   重来 ") + String::num_int64(model.deaths),
                HORIZONTAL_ALIGNMENT_RIGHT, 229, 13, MUTED);
    draw_string(font, Vector2(1000, 91), godot::String::utf8("ESC 暂停   ·   M 声音"),
                HORIZONTAL_ALIGNMENT_RIGHT, 239, 11, MUTED);
    if (model.boss_health > 0) {
        draw_rect(Rect2(328, 599, 624, 59), Color(.025, .05, .07, .9));
        centered(godot::String::utf8("监 刑 使  ·  执 朱 笔 者"), 622, 16, Color(.93, .62, .52), true);
        draw_rect(Rect2(352, 637, 576, 7), Color(.1, .09, .13, .95));
        draw_rect(Rect2(352, 637, 576.f * model.boss_health / model.boss_max, 7), RED);
        draw_rect(Rect2(348, 633, 584, 15), Color(.55, .35, .3), false, 1);
    }
    if (!model.hint.is_empty()) {
        draw_rect(Rect2(270, 673, 740, 34), Color(.02, .06, .09, .77));
        centered(model.hint, 696, 15, CREAM);
    }
    if (model.chapter_time > 0) {
        float a = std::min(1.f, model.chapter_time);
        Color c = CREAM;
        c.a = a;
        draw_rect(Rect2(36, 171, 3, 58), Color(.72, .43, .33, a));
        text(model.chapter, Vector2(57, 197), 24, c, true);
        c = MUTED;
        c.a = a;
        text(godot::String::utf8("雨未停，令未断。"), Vector2(59, 224), 13, c);
    }
}
void GameUI::draw_dialogue() {
    draw_rect(Rect2(0, 0, 1280, 116), Color(.014, .031, .05, .84));
    draw_rect(Rect2(0, 486, 1280, 234), Color(.014, .035, .056, .96));
    draw_line(Vector2(64, 487), Vector2(1216, 487), Color(.37, .51, .5), 1);
    draw_rect(Rect2(63, 516, 3, 116),
              line.speaker == godot::String::utf8("朱令") || line.speaker == godot::String::utf8("监刑使")
                  ? RED
                  : TEAL);
    Color speaker =
        line.speaker == godot::String::utf8("影十七") ? TEAL
        : line.speaker == godot::String::utf8("朱令") || line.speaker == godot::String::utf8("监刑使")
            ? Color(.94, .43, .38)
            : GOLD;
    text(line.speaker, Vector2(89, 539), 20, speaker, true);
    String shown = line.text.substr(0, std::min(int(line.text.length()), int(type_clock * 32)));
    draw_multiline_string(font, Vector2(89, 585), shown, HORIZONTAL_ALIGNMENT_LEFT, 1080, 26, -1, CREAM);
    text(line_complete() ? godot::String::utf8("E / ENTER  继续  ›")
                         : godot::String::utf8("E / ENTER  显示完整对白"),
         Vector2(993, 676), 13, MUTED);
    text(godot::String::utf8("听令，还是听自己。"), Vector2(89, 676), 12, Color(.36, .5, .52));
}
void GameUI::draw_overlay() {
    draw_rect(Rect2(0, 0, 1280, 720), Color(.012, .031, .047, .88));
    if (model.screen == Screen::Paused) {
        centered(godot::String::utf8("暂歇"), 261, 66, CREAM, true);
        centered(godot::String::utf8("雨还在下。命令可以等。"), 307, 18, MUTED);
        button(Rect2(465, 355, 350, 57), godot::String::utf8("继续  /  ESC"), true);
        button(Rect2(465, 431, 350, 57), godot::String::utf8("重来本章  /  R"));
        button(Rect2(465, 507, 350, 57), godot::String::utf8("返回卷首"));
    } else if (model.screen == Screen::Dead) {
        centered(godot::String::utf8("此令未成"), 280, 68, Color(.92, .59, .48), true);
        centered(godot::String::utf8("再试一次。这一刀，由你决定。"), 326, 20, CREAM);
        button(Rect2(465, 387, 350, 59), godot::String::utf8("重来本章  /  ENTER"), true);
        button(Rect2(465, 466, 350, 55), godot::String::utf8("返回卷首"));
    } else if (model.screen == Screen::Naming) {
        centered(godot::String::utf8("你的名字"), 260, 62, CREAM, true);
        centered(godot::String::utf8("守门人：天亮了。出城登记，报上姓名。"), 309, 20, MUTED);
        button(Rect2(442, 453, 396, 58), godot::String::utf8("签下自己的名字"), true);
        centered(model.error.is_empty() ? godot::String::utf8("这一次，没有人替你写。") : model.error, 554,
                 17, model.error.is_empty() ? GOLD : RED);
    } else if (model.screen == Screen::Complete) {
        centered(godot::String::utf8("无令之人"), 247, 76, CREAM, true);
        centered(model.name + godot::String::utf8("，天亮了。"), 323, 30, TEAL, true);
        centered(godot::String::utf8("刀上的旧名已经消失。往后的路，自己走。"), 377, 20, MUTED);
        centered(godot::String::utf8("斩敌 ") + String::num_int64(model.kills) +
                     godot::String::utf8("    ·    重来 ") + String::num_int64(model.deaths),
                 429, 15, GOLD);
        button(Rect2(465, 484, 350, 59), godot::String::utf8("返回卷首"), true);
        centered(godot::String::utf8("感谢你走完这一夜。"), 601, 16, CREAM);
    } else if (model.screen == Screen::Error) {
        centered(godot::String::utf8("卷宗无法打开"), 251, 46, CREAM, true);
        draw_multiline_string(font, Vector2(180, 330), model.error, HORIZONTAL_ALIGNMENT_LEFT, 920, 22, -1,
                              CREAM);
        button(Rect2(465, 484, 350, 59), godot::String::utf8("退出"));
    }
}
void GameUI::_draw() {
    if (font.is_null())
        return;
    if (model.screen == Screen::Title)
        draw_title();
    else {
        if (model.screen == Screen::Playing || model.screen == Screen::Dialogue)
            draw_hud();
        if (model.screen == Screen::Dialogue)
            draw_dialogue();
        else if (model.screen != Screen::Playing)
            draw_overlay();
    }
    if (model.flash > 0)
        draw_rect(Rect2(0, 0, 1280, 720), Color(.94, .96, .83, std::clamp(model.flash, 0.f, 1.f)));
    if (model.fade > 0)
        draw_rect(Rect2(0, 0, 1280, 720), Color(.01, .02, .04, std::clamp(model.fade, 0.f, 1.f)));
}
void GameUI::_gui_input(const Ref<InputEvent>& event) {
    Ref<InputEventMouseButton> mouse = event;
    if (mouse.is_null() || !mouse->is_pressed() || mouse->get_button_index() != MOUSE_BUTTON_LEFT)
        return;
    Vector2 p = mouse->get_position();
    String action;
    if (model.screen == Screen::Title) {
        if (Rect2(90, 487, 278, 59).has_point(p))
            action = "start";
        else if (model.has_save && Rect2(391, 487, 222, 59).has_point(p))
            action = "continue";
    } else if (model.screen == Screen::Paused) {
        if (Rect2(465, 355, 350, 57).has_point(p))
            action = "resume";
        else if (Rect2(465, 431, 350, 57).has_point(p))
            action = "restart";
        else if (Rect2(465, 507, 350, 57).has_point(p))
            action = "title";
    } else if (model.screen == Screen::Dead) {
        if (Rect2(465, 387, 350, 59).has_point(p))
            action = "restart";
        else if (Rect2(465, 466, 350, 55).has_point(p))
            action = "title";
    } else if (model.screen == Screen::Dialogue)
        action = "advance";
    else if (model.screen == Screen::Naming) {
        if (Rect2(442, 453, 396, 58).has_point(p))
            submit_name();
    } else if (model.screen == Screen::Complete) {
        if (Rect2(465, 484, 350, 59).has_point(p))
            action = "title";
    } else if (model.screen == Screen::Error) {
        if (Rect2(465, 484, 350, 59).has_point(p))
            action = "quit";
    }
    if (!action.is_empty() && on_action)
        on_action(action);
}
} // namespace zhan
