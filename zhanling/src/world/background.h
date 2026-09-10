#pragma once
#include <godot_cpp/classes/node2d.hpp>
#include <godot_cpp/classes/texture2d.hpp>
namespace zhan {
class Background : public godot::Node2D {
    GDCLASS(Background, godot::Node2D)
    godot::Ref<godot::Texture2D> sky, mountains, far_city, near_city, tower, branches, hero, platform;
    float clock = 0, camera_x = 0, daylight = 0;
    int chapter = 0;
    bool title = true;
    void tiled(const godot::Ref<godot::Texture2D>& texture, float offset, float y, godot::Color tint);

  protected:
    static void _bind_methods() {}

  public:
    void _ready() override;
    void _process(double dt) override;
    void _draw() override;
    void set_camera_x(float x) { camera_x = x; }
    void set_chapter(int value) { chapter = value; }
    void set_title(bool value) { title = value; }
    void set_daylight(float value) { daylight = value; }
};
} // namespace zhan
