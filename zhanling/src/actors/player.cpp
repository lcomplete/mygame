#include "actors/player.h"
#include "actors/actor_visual.h"
#include <cmath>
#include <godot_cpp/classes/collision_shape2d.hpp>
#include <godot_cpp/classes/input.hpp>
#include <godot_cpp/classes/rectangle_shape2d.hpp>
#include <godot_cpp/core/class_db.hpp>
using namespace godot;
namespace zhan {
void Player::_bind_methods() {
    ClassDB::bind_method(D_METHOD("health"), &Player::health);
}
void Player::configure(const MovementTuning& t) {
    tuning = t;
    life.reset(t.max_health);
}
void Player::_ready() {
    set_collision_layer(2);
    set_collision_mask(1);
    set_floor_snap_length(8);
    set_safe_margin(.1);
    auto* shape = memnew(CollisionShape2D);
    Ref<RectangleShape2D> box;
    box.instantiate();
    box->set_size(Vector2(30, 72));
    shape->set_shape(box);
    shape->set_position(Vector2(0, -36));
    add_child(shape);
    visual = memnew(ActorVisual);
    visual->configure("ninja");
    add_child(visual);
    add_to_group("player");
}
Rect2 Player::hurtbox() const {
    return Rect2(get_position() + Vector2(-15, -72), Vector2(30, 72));
}
void Player::restore() {
    life.reset(tuning.max_health);
    dash_left = dash_cd = attack_left = attack_cd = stagger = 0;
    set_velocity(Vector2());
    jump_window = {};
}
bool Player::hurt(int damage, Vector2 source) {
    if (dash_left > 0 || !life.damage(damage, tuning.hurt_invulnerability))
        return false;
    stagger = .15f;
    set_velocity(Vector2(get_position().x >= source.x ? 220 : -220, -190));
    if (visual)
        visual->hit_flash();
    if (on_hurt)
        on_hurt();
    if (!life.alive()) {
        if (on_sound)
            on_sound("death");
        if (on_died)
            on_died();
    } else if (on_sound)
        on_sound("hit");
    return true;
}
void Player::_physics_process(double delta) {
    float dt = float(delta);
    if (!visual || (is_frozen && is_frozen()))
        return;
    life.update(dt);
    tick(dash_cd, dt);
    tick(attack_cd, dt);
    tick(attack_left, dt);
    tick(stagger, dt);
    if (!life.alive()) {
        visual->set_rotation(.9);
        return;
    }
    Input* input = Input::get_singleton();
    float axis = locked ? 0.f : input->get_axis("move_left", "move_right");
    bool jump_pressed = !locked && input->is_action_just_pressed("jump");
    jump_window.update(dt, is_on_floor(), jump_pressed, tuning);
    Vector2 velocity = get_velocity();
    if (dash_left <= 0) {
        if (axis != 0 && stagger <= 0)
            facing = axis < 0 ? -1 : 1;
        if (stagger <= 0)
            velocity.x = approach(velocity.x, axis * tuning.speed,
                                  (std::abs(axis) > .1 ? tuning.acceleration : tuning.friction) * dt);
        velocity.y = std::min(velocity.y + tuning.gravity * dt, tuning.max_fall);
        if (!locked && jump_window.consume()) {
            velocity.y = -tuning.jump_speed;
            if (on_sound)
                on_sound("jump");
        } else if (jump_pressed && is_on_wall_only()) {
            velocity.y = -tuning.jump_speed * .93f;
            velocity.x = get_wall_normal().x * 420;
            stagger = .12f;
            if (on_sound)
                on_sound("jump");
        }
        if (!locked && input->is_action_just_released("jump") && velocity.y < -230)
            velocity.y = -230;
        if (!locked && input->is_action_just_pressed("dash") && dash_cd <= 0) {
            dash_left = tuning.dash_duration;
            dash_cd = tuning.dash_cooldown;
            if (on_sound)
                on_sound("dash");
        }
    }
    if (dash_left > 0) {
        tick(dash_left, dt);
        velocity = Vector2(facing * (dash_left > 0 ? tuning.dash_speed : tuning.speed), 0);
        trail_clock -= dt;
        if (trail_clock <= 0) {
            trail_clock = .027f;
            if (on_trail)
                on_trail(get_position(), facing);
        }
    }
    if (!locked && input->is_action_just_pressed("attack") && attack_cd <= 0) {
        attack_left = tuning.attack_duration;
        attack_cd = tuning.attack_cooldown;
        Vector2 origin = get_position() + Vector2(facing > 0 ? 0 : -tuning.attack_reach, -105);
        if (on_attack)
            on_attack(Rect2(origin, Vector2(tuning.attack_reach, 120)), facing);
        if (on_sound)
            on_sound("slash");
    }
    set_velocity(velocity);
    move_and_slide();
    String pose = attack_left > 0             ? "attack"
                  : dash_left > 0             ? "dash"
                  : !is_on_floor()            ? "jump"
                  : std::abs(velocity.x) > 30 ? "run"
                                              : "idle";
    visual->animate(pose, facing);
    visual->set_position(Vector2(0, crouched ? 22 : 0));
    visual->set_modulate(Color(1, 1, 1, life.immunity > 0 && int(life.immunity * 18) % 2 == 0 ? .38 : 1));
    if (get_position().y > 850) {
        life.immunity = 0;
        dash_left = 0;
        hurt(tuning.max_health, get_position());
    }
}
} // namespace zhan
