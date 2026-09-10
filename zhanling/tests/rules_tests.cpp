#include "core/rules.h"
#include <cstdlib>
#include <iostream>

static void require(bool test, const char* message) {
    if (!test) {
        std::cerr << "FAIL: " << message << '\n';
        std::exit(1);
    }
}
int main() {
    using namespace zhan;
    Vitality hp;
    hp.reset(5);
    require(hp.damage(2, 1), "first hit accepted");
    require(!hp.damage(2, 1) && hp.current == 3, "same-frame overlapping attacks do not stack");
    hp.update(.99f);
    require(!hp.damage(1, 1), "invulnerability lasts full interval");
    hp.update(.02f);
    require(hp.damage(99, 1) && hp.current == 0, "lethal damage clamps to zero");
    hp.update(5);
    require(!hp.damage(1, 1), "dead actors cannot be hit again");
    MovementTuning t;
    JumpWindow jump;
    jump.update(.01f, true, false, t);
    jump.update(.06f, false, true, t);
    require(jump.consume(), "coyote jump after leaving ledge");
    require(!jump.consume(), "jump cannot be consumed twice");
    jump.update(.01f, false, true, t);
    jump.update(.04f, true, false, t);
    require(jump.consume(), "buffered jump on landing");
    jump.update(.01f, false, true, t);
    jump.update(.2f, true, false, t);
    require(!jump.consume(), "expired buffer cannot trigger jump");
    BossPhases phases;
    require(!phases.update(11, 20), "boss stays in phase one above half HP");
    require(phases.update(10, 20), "boss enters phase two at half HP");
    require(!phases.update(5, 20), "phase change emits once");
    Progress p;
    p.room = 99;
    p.deaths = -1;
    p.sanitize(5);
    require(p.room == 4 && p.deaths == 0 && !p.advance(5), "invalid save safely clamps and cannot overflow");
    require(approach(0, 1, 20) == 1 && approach(10, 0, 20) == 0, "acceleration never overshoots");
    std::cout << "PASS: damage, invulnerability, jump grace/buffer, boss phases, save bounds, movement\n";
}
