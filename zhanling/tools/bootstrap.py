#!/usr/bin/env python3
"""Fetch the pinned official C++ bindings. Does not install anything globally."""
import pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parents[1]
REVISION = "6cceaf6a5f8b0d78ac5d71c139fd7fabba43b918"
target = ROOT / "third_party/godot-cpp"
if not (target / ".git").exists():
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "https://github.com/godotengine/godot-cpp.git", str(target)], check=True)
actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=target, text=True).strip()
if actual != REVISION:
    subprocess.run(["git", "fetch", "origin", REVISION, "--depth", "1"], cwd=target, check=True)
    subprocess.run(["git", "checkout", "--detach", REVISION], cwd=target, check=True)
print("godot-cpp:", REVISION, "(API target: 4.6)")
