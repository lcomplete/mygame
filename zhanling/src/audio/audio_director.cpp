#include "audio/audio_director.h"
#include <godot_cpp/classes/resource_loader.hpp>
using namespace godot;
namespace zhan {
void AudioDirector::configure(float m, float e) {
    music_db = m;
    effects_db = e;
}
void AudioDirector::_ready() {
    auto* l = ResourceLoader::get_singleton();
    music = memnew(AudioStreamPlayer);
    add_child(music);
    Ref<AudioStreamWAV> ambient = l->load("res://assets/audio/rain_city.wav");
    if (ambient.is_valid()) {
        ambient->set_loop_mode(AudioStreamWAV::LOOP_FORWARD);
        ambient->set_loop_begin(0);
        ambient->set_loop_end(16 * 22050);
        music->set_stream(ambient);
        music->set_volume_db(music_db);
        music->play();
    }
    for (int i = 0; i < 8; ++i) {
        auto* v = memnew(AudioStreamPlayer);
        v->set_volume_db(effects_db);
        add_child(v);
        voices.push_back(v);
    }
    for (const char* s : {"slash", "hit", "dash", "jump", "death", "glyph", "bell", "victory"})
        sounds[s] = l->load(String("res://assets/audio/") + s + ".wav");
}
void AudioDirector::play(const String& id) {
    if (muted || voices.empty())
        return;
    auto it = sounds.find(id);
    if (it == sounds.end() || it->second.is_null())
        return;
    auto* v = voices[next_voice++ % voices.size()];
    v->set_stream(it->second);
    v->play();
}
void AudioDirector::set_muted(bool value) {
    muted = value;
    if (music) {
        if (value)
            music->stop();
        else if (!music->is_playing())
            music->play();
    }
    for (auto* v : voices) {
        v->set_volume_db(effects_db);
        if (value)
            v->stop();
    }
}
void AudioDirector::_exit_tree() {
    if (music) {
        music->stop();
        music->set_stream(Ref<AudioStream>());
    }
    for (auto* v : voices) {
        v->stop();
        v->set_stream(Ref<AudioStream>());
    }
    sounds.clear();
}
} // namespace zhan
