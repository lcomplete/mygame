#pragma once
#include "core/game_data.h"
#include <functional>
#include <godot_cpp/classes/camera2d.hpp>
#include <godot_cpp/classes/node2d.hpp>
#include <godot_cpp/classes/system_font.hpp>
#include <godot_cpp/classes/texture2d.hpp>
namespace zhan {
class Player;
class Enemy;
class Effects;
struct Projectile {
    godot::Vector2 p, velocity;
    bool friendly = false;
    float life = 5;
};
struct Glyph {
    godot::Vector2 p;
    godot::String kind;
    float time, total;
    bool live = true;
};
class World : public godot::Node2D {
    GDCLASS(World, godot::Node2D)
    const GameData* data = nullptr;
    RoomData room;
    int room_index = 0;
    Player* player = nullptr;
    godot::Camera2D* camera = nullptr;
    Effects* effects = nullptr;
    std::vector<Enemy*> enemies;
    std::vector<godot::Vector2> seals;
    std::vector<Projectile> projectiles;
    std::vector<Glyph> glyphs;
    godot::Ref<godot::Texture2D> roof, lantern, banner, crate, scribe;
    godot::Ref<godot::SystemFont> font;
    float clock = 0, stop_time = 0, shake_time = 0, shake_power = 0;
    bool story_triggered = false, exiting = false, decree_live = true;
    void spawn_enemy(const Spawn& spawn);
    void add_platform(const godot::Rect2& rect);
    void damage_player(const godot::Rect2& rect, int damage, godot::Vector2 source);

  protected:
    static void _bind_methods() {}

  public:
    std::function<void()> on_exit, on_death, on_boss_defeated, on_phase, on_decree_cut;
    std::function<void(const godot::String&)> on_story, on_sound;
    std::function<void()> on_kill;
    void configure(const GameData* d, int index);
    void _ready() override;
    void _process(double dt) override;
    void _physics_process(double dt) override;
    void _draw() override;
    void strike(const godot::Rect2& rect, int facing);
    void shake(float strength, float duration = .16f);
    void command(const godot::String& kind, godot::Vector2 at);
    bool has_floor(godot::Vector2 p) const;
    bool clear() const;
    int remaining_enemies() const;
    int remaining_seals() const { return int(seals.size()); }
    Player* get_player() const { return player; }
    Enemy* get_boss() const;
    const std::vector<Enemy*>& get_enemies() const { return enemies; }
    const RoomData& get_room() const { return room; }
    float camera_left() const;
    godot::String hint() const;
    bool at_exit() const;
    bool decree_intact() const { return decree_live; }
    size_t command_count() const { return glyphs.size(); }
    const std::vector<Projectile>& get_projectiles() const { return projectiles; }
};
} // namespace zhan
