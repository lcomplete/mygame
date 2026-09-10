#include "world/effects.h"
#include "actors/actor_visual.h"
#include <algorithm>
#include <cmath>
#include <godot_cpp/classes/resource_loader.hpp>
using namespace godot;
namespace zhan {
float Effects::random() {
    seed = seed * 1664525u + 1013904223u;
    return float(seed & 0xffff) / 65535.f;
}
void Effects::_ready() {
    set_z_index(20);
    slash_tex = ResourceLoader::get_singleton()->load("res://assets/effects/slash_0.svg");
    trail_tex = ActorVisual::load_frame("ninja", "dash");
}
void Effects::burst(Vector2 at, Color tint, int count) {
    for (int i = 0; i < count; ++i) {
        float angle = random() * 6.283f, speed = 90 + random() * 380;
        float life = .2f + random() * .42f;
        particles.push_back(
            {at, Vector2(std::cos(angle), std::sin(angle)) * speed, tint, life, life, 1 + random() * 3});
    }
}
void Effects::slash(Vector2 at, int facing, bool enemy) {
    slashes.push_back({at, facing, .19f, .19f, enemy});
}
void Effects::trail(Vector2 at, int facing) {
    trails.push_back({at, facing, .23f});
}
void Effects::_process(double delta) {
    float dt = float(delta);
    for (auto& p : particles) {
        p.life -= dt;
        p.p += p.v * dt;
        p.v.y += 500 * dt;
    }
    for (auto& s : slashes)
        s.life -= dt;
    for (auto& t : trails)
        t.life -= dt;
    particles.erase(std::remove_if(particles.begin(), particles.end(), [](auto& p) { return p.life <= 0; }),
                    particles.end());
    slashes.erase(std::remove_if(slashes.begin(), slashes.end(), [](auto& s) { return s.life <= 0; }),
                  slashes.end());
    trails.erase(std::remove_if(trails.begin(), trails.end(), [](auto& t) { return t.life <= 0; }),
                 trails.end());
    queue_redraw();
}
void Effects::_draw() {
    for (auto& t : trails) {
        draw_set_transform(t.p, 0, Vector2(t.facing, 1));
        ActorVisual::draw_frame(this, trail_tex, ActorVisual::frame_rect(trail_tex),
                                Color(.45, .92, .86, t.life / .23f * .36f));
    }
    for (auto& s : slashes) {
        draw_set_transform(s.p, 0, Vector2(s.facing, 1));
        draw_texture_rect(slash_tex, Rect2(-25, -135, 190, 143), false,
                          s.enemy ? Color(1, .4, .35, s.life / s.total)
                                  : Color(.72, 1, .93, s.life / s.total));
    }
    draw_set_transform(Vector2(), 0, Vector2(1, 1));
    for (auto& p : particles) {
        Color c = p.color;
        c.a *= p.life / p.total;
        draw_line(p.p, p.p - p.v * .024f, c, p.size, true);
    }
}
} // namespace zhan
