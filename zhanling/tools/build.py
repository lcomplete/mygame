#!/usr/bin/env python3
"""Portable build entry point; uses CMake from PATH or the installed CLion bundle."""
import argparse, os, pathlib, shutil, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--run", action="store_true")
parser.add_argument("--editor", action="store_true")
parser.add_argument("--release", action="store_true")
args = parser.parse_args()
cmake = shutil.which("cmake") or "/Applications/CLion.app/Contents/bin/cmake/mac/bin/cmake"
if not pathlib.Path(cmake).exists():
    sys.exit("CMake 3.22+ is required. Install CMake, then run this script again.")
subprocess.run([sys.executable, str(ROOT / "tools/bootstrap.py")], check=True)
build = ROOT / "build"
build_type = "Release" if args.release else "Debug"
cache_file = build / "CMakeCache.txt"
cache = cache_file.read_text() if cache_file.exists() else ""
# Avoid unnecessarily regenerating all C++ bindings on every incremental build.
if "CMAKE_BUILD_TYPE:STRING=" + build_type not in cache:
    subprocess.run([cmake, "-S", str(ROOT), "-B", str(build), "-DCMAKE_BUILD_TYPE=" + build_type], check=True)
subprocess.run([cmake, "--build", str(build), "-j", str(min(os.cpu_count() or 4, 8))], check=True)
ctest = str(pathlib.Path(cmake).with_name("ctest"))
subprocess.run([ctest, "--test-dir", str(build), "--output-on-failure"], check=True)
godot = os.environ.get("ZHANLING_GODOT") or shutil.which("godot") or "/Applications/Godot.app/Contents/MacOS/Godot"
subprocess.run([godot, "--headless", "--path", str(ROOT / "game"), "--editor", "--import"], check=True)
if args.run or args.editor:
    subprocess.Popen([godot, "--path", str(ROOT / "game")] + (["--editor"] if args.editor else []))
