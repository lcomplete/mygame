#pragma once
#include <godot_cpp/variant/vector2.hpp>
namespace zhan {
class Game;
// Runs only when explicitly launched with --smoke-test. Never writes the player's save.
class IntegrationRunner {
    Game& game;
    int step = 0, frames = 0;
    float waited = 0;
    godot::Vector2 initial;
    int failures = 0;
    int jump_case = 0;
    bool jump_dashed = false;
    bool expect(bool condition, const char* message);
    void next();

  public:
    explicit IntegrationRunner(Game& g) : game(g) {}
    void update(float dt);
};
} // namespace zhan
