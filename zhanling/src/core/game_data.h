#pragma once
#include "core/rules.h"
#include <godot_cpp/variant/dictionary.hpp>
#include <godot_cpp/variant/rect2.hpp>
#include <godot_cpp/variant/string.hpp>
#include <godot_cpp/variant/vector2.hpp>
#include <vector>
namespace zhan {
struct EnemyTuning {
    int health = 2, damage = 1;
    float speed = 90, notice_range = 400, attack_range = 90, telegraph = .5f, recovery = .8f;
};
struct Spawn {
    godot::String kind;
    godot::Vector2 at;
    float left = 0, right = 0;
};
struct Hint {
    float x = 0;
    godot::String text;
};
struct RoomData {
    godot::String id, title, subtitle, objective, intro, story, next;
    float width = 2200, story_x = -1;
    godot::Vector2 spawn, exit, decree = godot::Vector2(-1, -1);
    std::vector<godot::Rect2> platforms;
    std::vector<Spawn> enemies;
    std::vector<godot::Vector2> seals, lanterns;
    std::vector<Hint> hints;
};
struct DialogueLine {
    godot::String speaker, text;
};
class GameData {
    godot::Dictionary enemy_values, story_values;

  public:
    MovementTuning movement;
    int player_damage = 2;
    float hit_stop = .045f, projectile_speed = 360, command_windup = 1.5f;
    float music_db = -13, effects_db = -7;
    std::vector<RoomData> rooms;
    godot::String error;
    bool load();
    int room_index(const godot::String& id) const;
    EnemyTuning enemy(const godot::String& kind) const;
    std::vector<DialogueLine> dialogue(const godot::String& id) const;
};
} // namespace zhan
