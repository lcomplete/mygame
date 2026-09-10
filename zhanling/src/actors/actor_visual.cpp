#include "actors/actor_visual.h"
#include <cmath>
#include <godot_cpp/classes/resource_loader.hpp>
using namespace godot;
namespace zhan {
void ActorVisual::draw_frame(CanvasItem* canvas, const Ref<Texture2D>& texture,
                             const Rect2& rect, const Color& tint) {
    if (texture.is_null())
        return;
    // Tightly packed generated poses can overlap a rectangular atlas region.
    // Source strips isolate the pose without changing or resampling the PNG.
    if (texture->has_meta("slices")) {
        Ref<Texture2D> source = texture->get_meta("source");
        const Array slices = texture->get_meta("slices");
        const Vector2 offset = texture->get_meta("offset");
        const Vector2 scale = rect.size / Vector2(texture->get_width(), texture->get_height());
        for (int i = 0; i < slices.size(); ++i) {
            const Rect2 slice = slices[i];
            canvas->draw_texture_rect_region(source,
                Rect2(rect.position + (slice.position + offset) * scale, slice.size * scale),
                slice, tint, false, true);
        }
        return;
    }
    canvas->draw_texture_rect(texture, rect, false, tint);
}
Rect2 ActorVisual::frame_rect(const Ref<Texture2D>& texture, float height) {
    const float width = texture.is_valid() && texture->get_height() > 0
                            ? height * texture->get_width() / texture->get_height()
                            : height;
    return Rect2(-width * .5f, -height * (102.f / 116.f), width, height);
}
Ref<Texture2D> ActorVisual::load_frame(const String& kind, const String& animation, int frame) {
    auto* loader = ResourceLoader::get_singleton();
    const String name = kind + String("_") + animation + String("_") + String::num_int64(frame);
    const String atlas_frame = "res://assets/characters/redesign/" + name + ".tres";
    if (loader->exists(atlas_frame)) {
        Ref<Texture2D> texture = loader->load(atlas_frame);
        if (texture.is_valid())
            return texture;
    }
    return loader->load("res://assets/characters/" + name + ".svg");
}
void ActorVisual::configure(const String& kind) {
    skin = kind;
    clips.clear();
    for (const auto& clip : std::vector<std::pair<String, int>>{
             {"idle", 2}, {"run", 6}, {"jump", 1}, {"attack", 3}, {"dash", 1}}) {
        auto& frames = clips[clip.first];
        for (int i = 0; i < clip.second; ++i)
            frames.push_back(load_frame(skin, clip.first, i));
    }
    scale_factor = kind == "magistrate" ? 1.55f : 1.f;
}
void ActorVisual::animate(const String& name, int direction) {
    if (pose != name) {
        pose = name;
        clock = 0;
    }
    facing = direction < 0 ? -1 : 1;
    set_scale(Vector2(facing * scale_factor, scale_factor));
}
Ref<Texture2D> ActorVisual::current_frame() const {
    auto it = clips.find(pose);
    if (it == clips.end() || it->second.empty())
        return {};
    float rate = pose == "run" ? 13.f : pose == "attack" ? 16.f : 2.f;
    int idx = int(clock * rate) % int(it->second.size());
    if (pose == "attack")
        idx = std::min(int(it->second.size()) - 1, int(clock * rate));
    return it->second[idx];
}
void ActorVisual::_process(double dt) {
    clock += dt;
    flash = std::max(0.f, flash - float(dt));
    queue_redraw();
}
void ActorVisual::_draw() {
    Ref<Texture2D> t = current_frame();
    if (t.is_null())
        return;
    Color tint = flash > 0 ? Color(3, 2.7, 2.2) : Color(1, 1, 1);
    draw_frame(this, t, frame_rect(t), tint);
}
} // namespace zhan
