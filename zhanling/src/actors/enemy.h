#pragma once
#include "core/game_data.h"
#include <functional>
#include <godot_cpp/classes/character_body2d.hpp>
namespace zhan {
class Player;
class ActorVisual;
class Enemy : public godot::CharacterBody2D {
    GDCLASS(Enemy, godot::CharacterBody2D)
    godot::String kind = "soldier";
    EnemyTuning tuning;
    Vitality life;
    BossPhases phases;
    ActorVisual* visual = nullptr;
    Player* target = nullptr;
    FoeState state = FoeState::Patrol;
    float state_time = 0, left = 0, right = 0, clock = 0;
    int facing = -1, action_count = 0;
    bool hit_sent = false;
    void enter(FoeState value, float duration);

  protected:
    static void _bind_methods() {}

  public:
    std::function<bool()> is_frozen;
    std::function<bool(godot::Vector2)> has_floor;
    std::function<void(const godot::Rect2&, int, godot::Vector2)> on_melee;
    std::function<void(godot::Vector2, godot::Vector2)> on_shoot;
    std::function<void(const godot::String&, godot::Vector2)> on_command;
    std::function<void(Enemy*)> on_died;
    std::function<void()> on_phase;
    std::function<void(godot::Vector2)> on_hit;
    void configure(const Spawn& spawn, const EnemyTuning& t, Player* player);
    void _ready() override;
    void _physics_process(double dt) override;
    void _draw() override;
    bool hurt(int damage, godot::Vector2 source);
    godot::Rect2 hurtbox() const;
    bool alive() const { return life.alive(); }
    bool boss() const { return kind == "magistrate"; }
    int health() const { return life.current; }
    int max_health() const { return life.maximum; }
    FoeState get_state() const { return state; }
};
} // namespace zhan
