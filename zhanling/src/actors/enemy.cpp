#include "actors/enemy.h"
#include "actors/actor_visual.h"
#include "actors/player.h"
#include <cmath>
#include <godot_cpp/classes/collision_shape2d.hpp>
#include <godot_cpp/classes/rectangle_shape2d.hpp>
using namespace godot;
namespace zhan {
void Enemy::configure(const Spawn& spawn, const EnemyTuning& t, Player* player) {
    kind = spawn.kind;
    tuning = t;
    life.reset(t.health);
    left = spawn.left;
    right = spawn.right;
    target = player;
    set_position(spawn.at);
}
void Enemy::_ready() {
    set_collision_layer(4);
    set_collision_mask(1);
    set_floor_snap_length(8);
    auto* shape = memnew(CollisionShape2D);
    Ref<RectangleShape2D> box;
    box.instantiate();
    box->set_size(Vector2(boss() ? 48 : 32, boss() ? 105 : 72));
    shape->set_shape(box);
    shape->set_position(Vector2(0, boss() ? -52.5 : -36));
    add_child(shape);
    visual = memnew(ActorVisual);
    visual->configure(kind);
    add_child(visual);
    add_to_group("enemies");
}
Rect2 Enemy::hurtbox() const {
    return Rect2(get_position() + Vector2(boss() ? -30 : -19, boss() ? -114 : -78),
                 Vector2(boss() ? 60 : 38, boss() ? 114 : 78));
}
void Enemy::enter(FoeState value, float duration) {
    state = value;
    state_time = duration;
    hit_sent = false;
}
bool Enemy::hurt(int damage, Vector2 source) {
    if (!life.damage(damage, boss() ? .1f : .12f))
        return false;
    if (visual)
        visual->hit_flash();
    if (on_hit)
        on_hit(get_position() + Vector2(0, -48));
    if (!life.alive()) {
        enter(FoeState::Dead, .38f);
        set_velocity(Vector2());
        if (on_died)
            on_died(this);
        return true;
    }
    // Boss armor preserves its telegraphs, preventing a permanent stagger lock.
    if (!boss()) {
        enter(FoeState::Stagger, .23f);
        set_velocity(Vector2(get_position().x >= source.x ? 170 : -170, -90));
    }
    if (boss() && phases.update(life.current, life.maximum) && on_phase)
        on_phase();
    return true;
}
void Enemy::_physics_process(double delta) {
    if (!target || !visual || (is_frozen && is_frozen()))
        return;
    float dt = float(delta);
    clock += dt;
    life.update(dt);
    tick(state_time, dt);
    queue_redraw();
    if (state == FoeState::Dead) {
        visual->set_modulate(Color(1, .65, .65, state_time / .38f));
        visual->set_rotation((.38f - state_time) * 2);
        if (state_time <= 0)
            hide();
        return;
    }
    Vector2 v = get_velocity();
    v.y = std::min(v.y + 1700 * dt, 1050.f);
    float dx = target->get_position().x - get_position().x;
    float dy = std::abs(target->get_position().y - get_position().y);
    bool aware = target->alive() && std::abs(dx) < tuning.notice_range && dy < (kind == "archer" ? 430 : 190);
    if (state == FoeState::Patrol) {
        if (aware)
            facing = dx < 0 ? -1 : 1;
        else if (get_position().x <= left)
            facing = 1;
        else if (get_position().x >= right)
            facing = -1;
        float attack_range = boss() && action_count % 3 == 1 ? 650 : tuning.attack_range;
        if (aware && std::abs(dx) < attack_range && is_on_floor()) {
            enter(FoeState::Telegraph, tuning.telegraph * (phases.enraged ? .78f : 1));
            v.x = 0;
        } else {
            v.x = facing * tuning.speed * (aware ? 1 : .5);
            if (kind == "archer" && aware)
                v.x = 0;
            bool edge = has_floor && !has_floor(get_position() + Vector2(facing * 35, 8));
            if (edge || (v.x < 0 && get_position().x <= left) || (v.x > 0 && get_position().x >= right))
                v.x = 0;
        }
    } else if (state == FoeState::Telegraph) {
        v.x = 0;
        if (state_time <= 0) {
            enter(FoeState::Attack, boss() ? .3f : .22f);
            if (kind == "archer") {
                if (on_shoot)
                    on_shoot(get_position() + Vector2(facing * 23, -55),
                             (target->get_position() + Vector2(0, -43) -
                              (get_position() + Vector2(facing * 23, -55)))
                                 .normalized());
                hit_sent = true;
            } else if (boss() && action_count % 3 == 1) {
                if (on_command)
                    on_command(phases.enraged && action_count % 2 == 0 ? "kill" : "stop",
                               target->get_position() + Vector2(0, -80));
                hit_sent = true;
            }
        }
    } else if (state == FoeState::Attack) {
        if (kind != "archer" && !(boss() && action_count % 3 == 1)) {
            v.x = facing * (boss() ? 570 : 270);
            if (has_floor && !has_floor(get_position() + Vector2(facing * 30, 8)))
                v.x = 0;
            if (!hit_sent && state_time < (boss() ? .21f : .14f)) {
                hit_sent = true;
                float reach = boss() ? 145 : 95;
                if (on_melee)
                    on_melee(Rect2(get_position() + Vector2(facing > 0 ? 0 : -reach, boss() ? -100 : -62),
                                   Vector2(reach, boss() ? 100 : 62)),
                             tuning.damage, get_position());
            }
        } else
            v.x = 0;
        if (state_time <= 0) {
            ++action_count;
            enter(FoeState::Recover, tuning.recovery * (phases.enraged ? .8f : 1));
        }
    } else if (state == FoeState::Recover) {
        v.x = approach(v.x, 0, 2200 * dt);
        if (state_time <= 0)
            enter(FoeState::Patrol, 0);
    } else if (state == FoeState::Stagger) {
        v.x = approach(v.x, 0, 650 * dt);
        if (state_time <= 0)
            enter(FoeState::Patrol, 0);
    }
    set_velocity(v);
    move_and_slide();
    visual->animate(state == FoeState::Attack ? "attack" : std::abs(v.x) > 20 ? "run" : "idle", facing);
    if (get_position().y > 830) {
        life.immunity = 0;
        hurt(999, get_position());
    }
}
void Enemy::_draw() {
    if (!alive())
        return;
    if (state == FoeState::Telegraph) {
        float y = boss() ? -152 : -113;
        draw_circle(Vector2(0, y), 10, Color(.9, .3, .3, .2));
        draw_line(Vector2(0, y - 6), Vector2(0, y + 2), Color(1, .68, .48), 3, true);
        draw_circle(Vector2(0, y + 7), 1.5, Color(1, .68, .48));
        draw_line(Vector2(0, -4), Vector2(facing * (boss() ? 155 : 95), -4), Color(.85, .3, .35, .7), 2,
                  true);
    }
    if (!boss() && life.current < life.maximum) {
        draw_rect(Rect2(-20, -95, 40, 3), Color(.1, .13, .18));
        draw_rect(Rect2(-20, -95, 40.f * life.current / life.maximum, 3), Color(.83, .41, .37));
    }
}
} // namespace zhan
