#pragma once
#include <algorithm>
#include <cmath>

namespace zhan {
// Engine-independent rules. Times are seconds; positions are Godot pixels.
struct MovementTuning {
    float speed = 310.f, acceleration = 2400.f, friction = 2800.f;
    float gravity = 1700.f, jump_speed = 640.f, max_fall = 1000.f;
    float coyote_time = .11f, jump_buffer = .13f;
    float dash_speed = 900.f, dash_duration = .16f, dash_cooldown = .55f;
    float attack_duration = .23f, attack_cooldown = .29f, attack_reach = 118.f;
    float hurt_invulnerability = 1.0f;
    int max_health = 5;
};
inline float approach(float value, float target, float step) {
    return value < target ? std::min(value + step, target) : std::max(value - step, target);
}
inline void tick(float& timer, float dt) {
    timer = std::max(0.f, timer - dt);
}

struct Vitality {
    int maximum = 5, current = 5;
    float immunity = 0;
    void reset(int hp) {
        maximum = std::max(1, hp);
        current = maximum;
        immunity = 0;
    }
    void update(float dt) { tick(immunity, dt); }
    bool damage(int amount, float immunity_seconds) {
        if (amount <= 0 || current <= 0 || immunity > 0)
            return false;
        current = std::max(0, current - amount);
        immunity = immunity_seconds;
        return true;
    }
    bool alive() const { return current > 0; }
};

struct JumpWindow {
    float grace = 0, buffered = 0;
    void update(float dt, bool grounded, bool pressed, const MovementTuning& t) {
        grace = grounded ? t.coyote_time : std::max(0.f, grace - dt);
        buffered = pressed ? t.jump_buffer : std::max(0.f, buffered - dt);
    }
    bool consume() {
        if (grace <= 0 || buffered <= 0)
            return false;
        grace = buffered = 0;
        return true;
    }
};

enum class FoeState { Patrol, Telegraph, Attack, Recover, Stagger, Dead };
struct BossPhases {
    bool enraged = false;
    bool update(int hp, int maximum) {
        if (!enraged && hp > 0 && hp * 2 <= maximum) {
            enraged = true;
            return true;
        }
        return false;
    }
};

struct Progress {
    int room = 0, deaths = 0, kills = 0;
    bool completed = false;
    bool advance(int count) {
        if (room + 1 >= count)
            return false;
        ++room;
        return true;
    }
    void sanitize(int room_count) {
        room = std::clamp(room, 0, std::max(0, room_count - 1));
        deaths = std::max(0, deaths);
    }
};
} // namespace zhan
