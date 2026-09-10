#!/bin/zsh
set -e
cd "${0:A:h}/.."
godot_bin="${ASHEN_OATH_GODOT:-/Applications/Godot.app/Contents/MacOS/Godot}"
"$godot_bin" --path game --editor --headless --import >/dev/null 2>&1
exec "$godot_bin" --path game
