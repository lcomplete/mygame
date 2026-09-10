#include "actors/actor_visual.h"
#include "actors/enemy.h"
#include "actors/player.h"
#include "audio/audio_director.h"
#include "core/game.h"
#include "ui/game_ui.h"
#include "world/background.h"
#include "world/effects.h"
#include "world/world.h"
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/godot.hpp>
using namespace godot;
// Editor-visible native node names; all gameplay code is C++.
class ZhanGame : public zhan::Game {
  GDCLASS(ZhanGame, zhan::Game) protected : static void _bind_methods() {}
};
void initialize_zhanling(ModuleInitializationLevel level) {
    if (level != MODULE_INITIALIZATION_LEVEL_SCENE)
        return;
    ClassDB::register_class<zhan::ActorVisual>();
    ClassDB::register_class<zhan::Player>();
    ClassDB::register_class<zhan::Enemy>();
    ClassDB::register_class<zhan::World>();
    ClassDB::register_class<zhan::Background>();
    ClassDB::register_class<zhan::Effects>();
    ClassDB::register_class<zhan::GameUI>();
    ClassDB::register_class<zhan::AudioDirector>();
    ClassDB::register_class<zhan::Game>();
    ClassDB::register_class<ZhanGame>();
}
void uninitialize_zhanling(ModuleInitializationLevel level) {
    (void)level;
}
extern "C" GDExtensionBool GDE_EXPORT
zhanling_library_init(GDExtensionInterfaceGetProcAddress get_proc_address, GDExtensionClassLibraryPtr library,
                      GDExtensionInitialization* initialization) {
    GDExtensionBinding::InitObject init(get_proc_address, library, initialization);
    init.register_initializer(initialize_zhanling);
    init.register_terminator(uninitialize_zhanling);
    init.set_minimum_library_initialization_level(MODULE_INITIALIZATION_LEVEL_SCENE);
    return init.init();
}
