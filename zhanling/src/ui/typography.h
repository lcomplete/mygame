#pragma once
#include <godot_cpp/classes/system_font.hpp>
#include <godot_cpp/variant/packed_string_array.hpp>
namespace zhan {
inline godot::Ref<godot::SystemFont> make_font(bool serif = false) {
    godot::Ref<godot::SystemFont> font;
    font.instantiate();
    godot::PackedStringArray names;
    if (serif) {
        names.push_back("Songti SC");
        names.push_back("Noto Serif CJK SC");
        names.push_back("SimSun");
    } else {
        names.push_back("PingFang SC");
        names.push_back("Noto Sans CJK SC");
        names.push_back("Microsoft YaHei");
    }
    names.push_back("sans-serif");
    font->set_font_names(names);
    return font;
}
} // namespace zhan
