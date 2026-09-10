#!/bin/zsh
set -eu
TASK_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ ! -f "$TASK_ROOT/game/bin/libzhanling.dylib" ]]; then
  python3 "$TASK_ROOT/tools/build.py"
fi
exec /Applications/Godot.app/Contents/MacOS/Godot --path "$TASK_ROOT/game"
