#pragma once
#include <godot_cpp/classes/node2d.hpp>
#include <godot_cpp/classes/texture2d.hpp>
#include <vector>
namespace zhan {
struct Particle {
    godot::Vector2 p, v;
    godot::Color color;
    float life, total, size;
};
struct SlashEffect {
    godot::Vector2 p;
    int facing;
    float life, total;
    bool enemy;
};
struct TrailEffect {
    godot::Vector2 p;
    int facing;
    float life;
};
class Effects : public godot::Node2D {
    GDCLASS(Effects, godot::Node2D)
    std::vector<Particle> particles;
    std::vector<SlashEffect> slashes;
    std::vector<TrailEffect> trails;
    godot::Ref<godot::Texture2D> slash_tex, trail_tex;
    unsigned seed = 1717;
    float random();

  protected:
    static void _bind_methods() {}

  public:
    void _ready() override;
    void _process(double dt) override;
    void _draw() override;
    void burst(godot::Vector2 at, godot::Color tint, int count = 16);
    void slash(godot::Vector2 at, int facing, bool enemy = false);
    void trail(godot::Vector2 at, int facing);
};
} // namespace zhan
