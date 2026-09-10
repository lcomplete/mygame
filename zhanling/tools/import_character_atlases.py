#!/usr/bin/env python3
"""Create Godot frame resources without resampling or changing generated PNG pixels."""
import argparse
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "game/assets/characters/redesign"
KINDS = ("ninja", "soldier", "archer", "magistrate", "scribe")
CLIPS = {"idle": (0, 1), "run": (2, 3, 4, 5, 6, 7),
         "jump": (8,), "attack": (9, 10, 11), "dash": (12,)}


def png_size(path):
    header = path.read_bytes()[:33]
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"Not a PNG image: {path}")
    width, height = struct.unpack(">II", header[16:24])
    if header[25] not in (4, 6):
        raise ValueError(f"Expected a PNG with an alpha channel: {path}")
    if width != height:
        raise ValueError(f"Expected a square 4 by 4 atlas: {path} ({width}x{height})")
    return width, height


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate resources without writing")
    args = parser.parse_args()
    # Optional per-frame source rectangles and margins calibrate generated layout.
    layout_path = ART / "layout.json"
    layout = json.loads(layout_path.read_text()) if layout_path.exists() else {}
    pending = {}
    for kind in KINDS:
        width, height = png_size(ART / f"{kind}.png")
        boundaries = [round(i * width / 4) for i in range(5)]
        for pose, indices in CLIPS.items():
            for frame, index in enumerate(indices):
                name = f"{kind}_{pose}_{frame}"
                spec = layout.get(name, {})
                col, row = index % 4, index // 4
                region = spec.get("region", [boundaries[col], boundaries[row],
                                  boundaries[col + 1] - boundaries[col],
                                  boundaries[row + 1] - boundaries[row]])
                x, y, w, h = region
                if min(x, y) < 0 or min(w, h) <= 0 or x + w > width or y + h > height:
                    raise ValueError(f"Invalid source rectangle for {name}: {region}")
                margin = spec.get("margin", [0, 0, 0, 0])
                rect = ", ".join(str(v) for v in region)
                pad = ", ".join(str(v) for v in margin)
                pending[ART / f"{name}.tres"] = (
                    '[gd_resource type="AtlasTexture" load_steps=2 format=3]\n\n'
                    f'[ext_resource type="Texture2D" path="res://assets/characters/redesign/{kind}.png" id="1"]\n\n'
                    '[resource]\n'
                    'atlas = ExtResource("1")\n'
                    f'region = Rect2({rect})\n'
                    f'margin = Rect2({pad})\n'
                    'filter_clip = true\n'
                )
                if "slices" in spec:
                    slices = spec["slices"]
                    for sx, sy, sw, sh in slices:
                        if sx < x or sy < y or sw <= 0 or sh <= 0 or sx + sw > x + w or sy + sh > y + h:
                            raise ValueError(f"Slice outside source rectangle: {name}")
                    serialized = ", ".join("Rect2(" + ", ".join(map(str, r)) + ")" for r in slices)
                    pending[ART / f"{name}.tres"] += (
                        'metadata/source = ExtResource("1")\n'
                        f'metadata/offset = Vector2({margin[0] - x}, {margin[1] - y})\n'
                        f'metadata/slices = [{serialized}]\n'
                    )
    for path, content in pending.items():
        if args.check:
            if not path.exists() or path.read_text() != content:
                raise ValueError(f"Missing or outdated frame resource: {path}")
        else:
            path.write_text(content)
    print(f"{'Verified' if args.check else 'Wrote'} {len(pending)} frames from {len(KINDS)} original PNG atlases.")


if __name__ == "__main__":
    main()
