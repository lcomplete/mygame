#pragma once
#include "core/rules.h"
#include <functional>
#include <godot_cpp/classes/character_body2d.hpp>
namespace zhan {
class ActorVisual;
class Player : public godot::CharacterBody2D {
    GDCLASS(Player, godot::CharacterBody2D)
    MovementTuning tuning;
    Vitality life;
    JumpWindow jump_window;
    ActorVisual* visual = nullptr;
    float dash_left = 0, dash_cd = 0, attack_left = 0, attack_cd = 0, stagger = 0, trail_clock = 0;
    int facing = 1;
    bool locked = false, crouched = false;

  protected:
    static void _bind_methods();

  public:
    std::function<void(const godot::Rect2&, int)> on_attack;
    std::function<void(const godot::String&)> on_sound;
    std::function<void(godot::Vector2, int)> on_trail;
    std::function<void()> on_hurt, on_died;
    std::function<bool()> is_frozen;
    void configure(const MovementTuning& t);
    void _ready() override;
    void _physics_process(double dt) override;
    bool hurt(int damage, godot::Vector2 source);
    void lock(bool value) { locked = value; }
    void kneel(bool value) { crouched = value; }
    bool alive() const { return life.alive(); }
    int health() const { return life.current; }
    int max_health() const { return life.maximum; }
    int direction() const { return facing; }
    bool dashing() const { return dash_left > 0; }
    float dash_ready() const { return 1.f - dash_cd / tuning.dash_cooldown; }
    godot::Rect2 hurtbox() const;
    ActorVisual* get_visual() const { return visual; }
    void restore();
};
} // namespace zhan
