# 斩令 · SEVER THE DECREE

一个东方雨夜题材的横版动作短篇。影武者奉令潜入印诏司，最终用自己的刀斩断控制自己的诏令，取回名字。

**Godot 4.6.2 + C++17 GDExtension。游戏逻辑没有使用 GDScript。**

## 本机运行

首次编译（Python 仅用于构建及素材工具）：

```sh
cd /Users/lcomplete/code/mygame/zhanling
python3 tools/build.py --run
```

已有编译产物时，双击 `tools/run.command`；或在 Godot 4.6.2 中打开 `game/project.godot`，按 F6/F5 运行。

```sh
python3 tools/build.py --editor
```

`tools/build.py` 优先使用 PATH 中的 CMake，也能找到本机 CLion 内置的 CMake。编译器使用 Xcode Command Line Tools 的 Clang。Godot 可通过 `ZHANLING_GODOT` 环境变量指定路径。

如果出现 `Can't open GDExtension dynamic library`，先运行构建命令，确认 `game/bin/libzhanling.dylib` 存在。Godot 不会自动编译 C++。若编辑器在首次构建前已经打开，构建结束后重新打开该项目，让它重新注册原生节点。

## 操作

| 操作 | 键盘 | 手柄 |
|---|---|---|
| 移动 | A / D 或左右方向键 | 左摇杆 / 十字键 |
| 跳跃、蹬墙 | Space / W / 上 | A |
| 斩击、斩符、弹反箭矢 | J | X |
| 突进（短暂无敌） | Shift / K | B |
| 章节出口交互 | E | Y |
| 对白继续 | E / Enter / 鼠标点击 | 使用键盘或鼠标 |
| 暂停 | Esc | 使用键盘 |
| 重来本章 | 死亡后 Enter，或暂停时 R | 使用键盘 |
| 声音开关 | M | 使用键盘 |
| 全屏 | F11 | 使用键盘 |

角色具有跳跃输入缓冲、离地宽限、短跳、蹬墙、受伤无敌和快速重试。敌人攻击有明显预警。斩击可以打回箭矢，也能阻止 Boss 的文字法术。每一章入口恢复生命并保存进度。

## 内容与修改入口

- 五个章节：雨门、无名街、藏令阁、最后一道命令、无令之人。
- 刀兵、弓手，以及具有两个战斗阶段的监刑使。
- 完整的开场、途中对白、反转、最终斩令、命名结局。
- 菜单、继续、暂停、死亡重试、静音、章节存档。
- 五类手绘角色：5 张 AI 生成的透明 PNG 动作图集、65 个游戏动画帧；保留 80 个原有 SVG 与 9 个合成 WAV 音频。

| 想修改什么 | 文件 |
|---|---|
| 角色速度、跳跃、攻击、突进 | `game/data/tuning.json` |
| 敌人血量、攻击预警、Boss 数值 | `game/data/tuning.json` |
| 平台、敌人、出口、封印、提示位置 | `game/data/rooms.json` |
| 全部对白 | `game/data/story.json` |
| 角色造型与动画姿势 | `game/assets/characters/redesign/`；设计与实际提示词见 `docs/CHARACTER_REDESIGN.md` |
| 角色图集分帧与落脚点 | `game/assets/characters/redesign/layout.json`、`tools/import_character_atlases.py` |
| 场景图像与音频 | `tools/draw_assets.py` |
| UI 排版、字体与菜单 | `src/ui/game_ui.cpp` |
| 角色与敌人行为 | `src/actors/` |
| 整体流程与存档 | `src/core/game.cpp` |

修改关卡 JSON 后重启游戏即可。修改 PNG / SVG 后 Godot 自动重新导入。修改 C++ 后重新构建。调整角色图集分帧后执行 `python3 tools/import_character_atlases.py`。角色重设计说明见 [角色美术文档](docs/CHARACTER_REDESIGN.md)。

重新生成原有 SVG、场景与音频（不会覆盖新角色 PNG）：

```sh
python3 tools/draw_assets.py
```

源代码组织、扩展方式、数据约定和测试说明见 [架构文档](docs/ARCHITECTURE.md)。

## 验证

```sh
# 基础规则：不依赖 Godot，也不需要 godot-cpp
cmake -S . -B build-rules -DZHANLING_BUILD_GAME=OFF
cmake --build build-rules
ctest --test-dir build-rules --output-on-failure

# 在真实 Godot 引擎中验证输入、物理、战斗、Boss、流程和结局
/Applications/Godot.app/Contents/MacOS/Godot --headless --path game -- --smoke-test
```

集成测试写入独立的 `user://integration_progress.cfg`，不会覆盖玩家进度。正常存档在 `user://progress.cfg`，由 Godot 保管。截图和关卡预览：

```sh
mkdir -p artifacts
/Applications/Godot.app/Contents/MacOS/Godot --path game -- --capture=/tmp/zhanling-title.png
/Applications/Godot.app/Contents/MacOS/Godot --path game -- --room=3 --capture=/tmp/zhanling-boss.png
```

`--room` 为开发预览入口，使用独立存档；编号从 0 开始。

## 平台与素材

当前本机编译目标是 **macOS arm64**。源码和扩展路径也预留 Linux / Windows，但没有在这些平台编译验证；分发前需要分别构建对应平台的动态库。当前采用 GL Compatibility 渲染。

角色图集由内置图像生成工具为本项目绘制，完整提示词与原图均随项目保存；场景、视觉特效、音效与背景音乐由项目工具绘制或合成，没有使用商业游戏素材。中文排版使用操作系统字体（macOS 优先宋体、苹方）；跨平台建议安装 Noto CJK 字体。字体文件没有被复制或重新分发。

官方 `godot-cpp` 依赖使用 MIT 许可，固定提交见 `tools/bootstrap.py`。参考文档：[Godot 4.6 C++ GDExtension](https://docs.godotengine.org/en/4.6/tutorials/scripting/cpp/gdextension_cpp_example.html)。
