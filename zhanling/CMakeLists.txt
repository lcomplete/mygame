cmake_minimum_required(VERSION 3.22)
project(Zhanling VERSION 0.1.0 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

option(ZHANLING_BUILD_GAME "Build the Godot GDExtension" ON)
include(CTest)
if(BUILD_TESTING)
  add_executable(rules_tests tests/rules_tests.cpp)
  target_include_directories(rules_tests PRIVATE src)
  add_test(NAME gameplay_rules COMMAND rules_tests)
endif()

if(ZHANLING_BUILD_GAME)
  if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/third_party/godot-cpp/CMakeLists.txt")
    message(FATAL_ERROR "Run python3 tools/bootstrap.py first.")
  endif()
  set(GODOTCPP_API_VERSION "4.6" CACHE STRING "Godot API version")
  set(GODOTCPP_TARGET "template_debug" CACHE STRING "Godot build target")
  set(GODOTCPP_BUILD_PROFILE "${CMAKE_CURRENT_SOURCE_DIR}/build_profile.json" CACHE FILEPATH "")
  add_subdirectory(third_party/godot-cpp EXCLUDE_FROM_ALL)
  add_library(zhanling SHARED
    src/register_types.cpp
    src/core/game.cpp
    src/core/game_data.cpp
    src/actors/actor_visual.cpp
    src/actors/player.cpp
    src/actors/enemy.cpp
    src/world/world.cpp
    src/world/background.cpp
    src/world/effects.cpp
    src/ui/game_ui.cpp
    src/audio/audio_director.cpp
    tests/integration_runner.cpp)
  target_include_directories(zhanling PRIVATE src)
  target_link_libraries(zhanling PRIVATE godot-cpp)
  target_compile_options(zhanling PRIVATE $<$<CXX_COMPILER_ID:AppleClang,Clang,GNU>:-Wall;-Wextra;-Wpedantic;-Wno-unused-parameter>)
  set_target_properties(zhanling PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/game/bin"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/game/bin"
    OUTPUT_NAME zhanling)
endif()
