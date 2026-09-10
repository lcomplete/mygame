#pragma once
#include <godot_cpp/classes/node2d.hpp>
#include <godot_cpp/classes/texture2d.hpp>
#include <map>
#include <vector>
namespace zhan {
class ActorVisual : public godot::Node2D {
    GDCLASS(ActorVisual, godot::Node2D)
    std::map<godot::String, std::vector<godot::Ref<godot::Texture2D>>> clips;
    godot::String skin = "ninja", pose = "idle";
    float clock = 0, flash = 0, scale_factor = 1;
    int facing = 1;

  protected:
    static void _bind_methods() {}

  public:
    static godot::Ref<godot::Texture2D> load_frame(const godot::String& kind,
                                                 const godot::String& animation,
                                                 int frame = 0);
    static godot::Rect2 frame_rect(const godot::Ref<godot::Texture2D>& texture,
                                  float height = 116.f);
    static void draw_frame(godot::CanvasItem* canvas, const godot::Ref<godot::Texture2D>& texture,
                           const godot::Rect2& rect,
                           const godot::Color& tint = godot::Color(1, 1, 1));
    void configure(const godot::String& kind);
    void animate(const godot::String& name, int direction);
    void hit_flash() { flash = .13f; }
    void _process(double dt) override;
    void _draw() override;
    void set_scale_factor(float s) { scale_factor = s; }
    godot::Ref<godot::Texture2D> current_frame() const;
};
} // namespace zhan
