#include "world/background.h"
#include "actors/actor_visual.h"
#include <cmath>
#include <godot_cpp/classes/resource_loader.hpp>
using namespace godot;
namespace zhan {
void Background::_ready() {
    auto* l = ResourceLoader::get_singleton();
    sky = l->load("res://assets/environment/sky.svg");
    mountains = l->load("res://assets/environment/mountains.svg");
    far_city = l->load("res://assets/environment/city_far.svg");
    near_city = l->load("res://assets/environment/city_near.svg");
    tower = l->load("res://assets/environment/tower.svg");
    branches = l->load("res://assets/environment/branches.svg");
    hero = ActorVisual::load_frame("ninja", "idle");
    platform = l->load("res://assets/environment/platform.svg");
}
void Background::_process(double dt) {
    clock += dt;
    queue_redraw();
}
void Background::tiled(const Ref<Texture2D>& tex, float offset, float y, Color tint) {
    if (tex.is_null())
        return;
    float x = -std::fmod(offset, 2560.f);
    draw_texture_rect(tex, Rect2(x, y, 2560, 720), false, tint);
    if (x + 2560 < 1280)
        draw_texture_rect(tex, Rect2(x + 2560, y, 2560, 720), false, tint);
}
void Background::_draw() {
    if (sky.is_null())
        return;
    draw_texture_rect(sky, Rect2(0, 0, 1280, 720), false);
    if (daylight > 0)
        draw_rect(Rect2(0, 0, 1280, 720), Color(.63, .48, .35, daylight * .72f));
    Vector2 moon(964 - camera_x * .014f, 171);
    for (int i = 5; i > 0; --i)
        draw_circle(moon, 64 + i * 13, Color(.7, .84, .76, .013));
    draw_circle(moon, 59, Color(.68, .78, .69, .92));
    draw_circle(moon + Vector2(-9, -5), 59, Color(.18, .31, .36, .86));
    tiled(mountains, camera_x * .10f, 0, Color(1, 1, 1));
    tiled(far_city, camera_x * .23f, 25, Color(1, 1, 1));
    if (chapter >= 2 || title)
        draw_texture_rect(tower, Rect2(title ? 800 : 790 - camera_x * .05f, title ? 115 : 80, 330, 480),
                          false, Color(.7, .9, .91, .86));
    tiled(near_city, camera_x * .44f, 95, Color(.83, .98, 1, .9));
    // Transparent cloud bands move slowly between buildings and the foreground.
    for (int i = 0; i < 8; ++i) {
        float y = 360 + i * 35 + std::sin(clock * .12f + i) * 7;
        draw_rect(Rect2(0, y, 1280, 14), Color(.42, .64, .65, .025f));
    }
    if (title) {
        draw_texture_rect(platform, Rect2(705, 568, 800, 190), true, Color(.6, .77, .79));
        Rect2 hero_rect = ActorVisual::frame_rect(hero, 250);
        hero_rect.position += Vector2(1043, 570);
        ActorVisual::draw_frame(this, hero, hero_rect);
        draw_line(Vector2(748, 567), Vector2(1280, 567), Color(.6, .82, .81, .7), 2, true);
    }
    draw_texture_rect(branches, Rect2(-130, -32, 460, 290), false, Color(1, 1, 1, .85));
    // Stable deterministic rain avoids allocations and never affects game simulation.
    for (int i = 0; i < 155; ++i) {
        float speed = 250 + (i % 7) * 42;
        float x = std::fmod(i * 137.3f - clock * 80 + 20000, 1420.f) - 70;
        float y = std::fmod(i * 79.7f + clock * speed, 820.f) - 50;
        draw_line(Vector2(x, y), Vector2(x - 7, y + 18 + i % 10),
                  Color(.57, .77, .8, (.055f + (i % 3) * .025f) * (1 - daylight)), 1, true);
    }
    // Framing darkens edges without hiding the playfield.
    for (int i = 0; i < 10; ++i) {
        float a = .026f;
        draw_rect(Rect2(0, i * 5, 1280, 5), Color(.015, .035, .06, a * (10 - i)));
        draw_rect(Rect2(0, 720 - i * 6 - 6, 1280, 6), Color(.01, .02, .04, a * (10 - i)));
    }
}
} // namespace zhan
