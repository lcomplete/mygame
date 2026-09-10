#include "core/game_data.h"
#include <godot_cpp/classes/file_access.hpp>
#include <godot_cpp/classes/json.hpp>
#include <godot_cpp/variant/array.hpp>
using namespace godot;
namespace zhan {
static Dictionary read_json(const String& path, String& error) {
    Ref<FileAccess> file = FileAccess::open(path, FileAccess::READ);
    if (file.is_null()) {
        error = godot::String::utf8("无法读取 ") + path;
        return {};
    }
    Ref<JSON> json;
    json.instantiate();
    if (json->parse(file->get_as_text()) != OK) {
        error = path + String(": ") + json->get_error_message();
        return {};
    }
    Variant result = json->get_data();
    if (result.get_type() != Variant::DICTIONARY) {
        error = path + String(godot::String::utf8(": 顶层必须是对象"));
        return {};
    }
    return result;
}
static Vector2 vec(const Variant& v) {
    Array a = v;
    return a.size() >= 2 ? Vector2(float(a[0]), float(a[1])) : Vector2();
}
bool GameData::load() {
    error = "";
    rooms.clear();
    Dictionary tuning = read_json("res://data/tuning.json", error);
    if (!error.is_empty())
        return false;
    Dictionary p = tuning.get("player", Dictionary());
    movement.speed = float(p.get("speed", movement.speed));
    movement.acceleration = float(p.get("acceleration", movement.acceleration));
    movement.friction = float(p.get("friction", movement.friction));
    movement.gravity = float(p.get("gravity", movement.gravity));
    movement.jump_speed = float(p.get("jump_speed", movement.jump_speed));
    movement.max_fall = float(p.get("max_fall", movement.max_fall));
    movement.coyote_time = float(p.get("coyote_time", movement.coyote_time));
    movement.jump_buffer = float(p.get("jump_buffer", movement.jump_buffer));
    movement.dash_speed = float(p.get("dash_speed", movement.dash_speed));
    movement.dash_duration = float(p.get("dash_duration", movement.dash_duration));
    movement.dash_cooldown = float(p.get("dash_cooldown", movement.dash_cooldown));
    movement.attack_duration = float(p.get("attack_duration", movement.attack_duration));
    movement.attack_cooldown = float(p.get("attack_cooldown", movement.attack_cooldown));
    movement.attack_reach = float(p.get("attack_reach", movement.attack_reach));
    movement.hurt_invulnerability = float(p.get("hurt_invulnerability", movement.hurt_invulnerability));
    movement.max_health = int(p.get("max_health", 5));
    if (movement.max_health < 1 || movement.speed <= 0 || movement.gravity <= 0 ||
        movement.attack_cooldown <= 0) {
        error = godot::String::utf8("tuning.json: 血量、速度、重力和攻击间隔必须大于零");
        return false;
    }
    enemy_values = tuning.get("enemies", Dictionary());
    Dictionary combat = tuning.get("combat", Dictionary());
    player_damage = int(combat.get("player_damage", 2));
    hit_stop = float(combat.get("hit_stop", .045));
    projectile_speed = float(combat.get("projectile_speed", 360));
    command_windup = float(combat.get("command_windup", 1.5));
    Dictionary audio = tuning.get("audio", Dictionary());
    music_db = float(audio.get("music_db", -13));
    effects_db = float(audio.get("effects_db", -7));
    Dictionary root = read_json("res://data/rooms.json", error);
    if (!error.is_empty())
        return false;
    Array all = root.get("rooms", Array());
    for (int i = 0; i < all.size(); ++i) {
        Dictionary d = all[i];
        RoomData r;
        r.id = d.get("id", "");
        r.next = d.get("next", "");
        if (r.id.is_empty() || room_index(r.id) >= 0) {
            error = String::utf8("关卡 ID 不能为空或重复");
            return false;
        }
        r.title = d.get("title", "");
        r.subtitle = d.get("subtitle", "");
        r.objective = d.get("objective", "");
        r.intro = d.get("intro", "");
        r.story = d.get("story", "");
        r.width = float(d.get("width", 2200));
        r.story_x = float(d.get("story_x", -1));
        r.spawn = vec(d.get("spawn", Array()));
        r.exit = vec(d.get("exit", Array()));
        if (d.has("decree"))
            r.decree = vec(d["decree"]);
        Array platforms = d.get("platforms", Array());
        for (int k = 0; k < platforms.size(); ++k) {
            Array a = platforms[k];
            if (a.size() != 4) {
                error = godot::String::utf8("平台数据必须是 [x,y,w,h]");
                return false;
            }
            Rect2 rect{float(a[0]), float(a[1]), float(a[2]), float(a[3])};
            if (rect.size.x <= 0 || rect.size.y <= 0) {
                error = godot::String::utf8("平台尺寸必须为正数");
                return false;
            }
            r.platforms.push_back(rect);
        }
        Array foes = d.get("enemies", Array());
        for (int k = 0; k < foes.size(); ++k) {
            Dictionary s = foes[k];
            Spawn spawn;
            spawn.kind = s.get("kind", "soldier");
            spawn.at = vec(s.get("at", Array()));
            Vector2 patrol = vec(s.get("patrol", Array()));
            spawn.left = patrol.x;
            spawn.right = patrol.y;
            if (!enemy_values.has(spawn.kind)) {
                error = godot::String::utf8("未知敌人类型: ") + spawn.kind;
                return false;
            }
            r.enemies.push_back(spawn);
        }
        for (const char* key : {"seals", "lanterns"}) {
            Array a = d.get(key, Array());
            for (int k = 0; k < a.size(); ++k)
                (String(key) == "seals" ? r.seals : r.lanterns).push_back(vec(a[k]));
        }
        Array hints = d.get("hints", Array());
        for (int k = 0; k < hints.size(); ++k) {
            Dictionary h = hints[k];
            r.hints.push_back({float(h.get("at", 0)), h.get("text", "")});
        }
        if (r.width < 1280 || r.platforms.empty()) {
            error = godot::String::utf8("关卡宽度至少 1280，且必须有平台");
            return false;
        }
        rooms.push_back(r);
    }
    if (rooms.empty()) {
        error = godot::String::utf8("rooms.json 至少需要一个关卡");
        return false;
    }
    story_values = read_json("res://data/story.json", error);
    if (!error.is_empty())
        return false;
    for (const auto& room : rooms) {
        if (!room.next.is_empty() && room_index(room.next) < 0) {
            error = String::utf8("未知后续关卡: ") + room.next;
            return false;
        }
        for (const String& id : {room.intro, room.story})
            if (!id.is_empty() && !story_values.has(id)) {
                error = String::utf8("未知对白: ") + id;
                return false;
            }
    }
    return true;
}
int GameData::room_index(const String& id) const {
    for (size_t i = 0; i < rooms.size(); ++i)
        if (rooms[i].id == id)
            return int(i);
    return -1;
}
EnemyTuning GameData::enemy(const String& kind) const {
    Dictionary d = enemy_values.get(kind, Dictionary());
    EnemyTuning t;
    t.health = int(d.get("health", 2));
    t.damage = int(d.get("damage", 1));
    t.speed = float(d.get("speed", 90));
    t.notice_range = float(d.get("notice_range", 400));
    t.attack_range = float(d.get("attack_range", 90));
    t.telegraph = float(d.get("telegraph", .5));
    t.recovery = float(d.get("recovery", .8));
    return t;
}
std::vector<DialogueLine> GameData::dialogue(const String& id) const {
    std::vector<DialogueLine> lines;
    Array a = story_values.get(id, Array());
    for (int i = 0; i < a.size(); ++i) {
        Dictionary d = a[i];
        lines.push_back({d.get("speaker", ""), d.get("text", "")});
    }
    return lines;
}
} // namespace zhan
