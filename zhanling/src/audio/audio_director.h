#pragma once
#include <godot_cpp/classes/audio_stream_player.hpp>
#include <godot_cpp/classes/audio_stream_wav.hpp>
#include <godot_cpp/classes/node.hpp>
#include <map>
#include <vector>
namespace zhan {
class AudioDirector : public godot::Node {
    GDCLASS(AudioDirector, godot::Node)
    godot::AudioStreamPlayer* music = nullptr;
    std::vector<godot::AudioStreamPlayer*> voices;
    std::map<godot::String, godot::Ref<godot::AudioStreamWAV>> sounds;
    int next_voice = 0;
    bool muted = false;
    float music_db = -13, effects_db = -7;

  protected:
    static void _bind_methods() {}

  public:
    void _ready() override;
    void _exit_tree() override;
    void configure(float music_volume, float effects_volume);
    void play(const godot::String& id);
    void set_muted(bool value);
    bool is_muted() const { return muted; }
};
} // namespace zhan
