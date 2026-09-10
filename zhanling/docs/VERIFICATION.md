# 本机验证记录

- 环境：Godot 4.6.2.stable.official.71f334935，macOS arm64（Apple M1 Pro）。
- C++17 / Apple Clang 编译通过，GDExtension 动态库成功加载。
- `python3 tools/build.py` 完整构建、规则测试和 Godot 资源导入通过。
- 纯 C++ 规则测试通过。
- Godot 引擎内集成测试：44 个断言通过，包含真实输入、移动、跳跃、落地、受伤无敌、突进无敌、斩击、封印、暂停、五章流程、Boss 阶段、法术打断、终章斩令、Unicode 名字、独立存档。
- 9 条关键断桥/上升平台路线由实际角色控制器通过。
- 弓手箭矢实际命中、实际斩击反射、反射箭矢反伤通过。
- 80 个 SVG 与 3 个 JSON 数据文件解析通过。
- 主菜单、战斗场景与 Boss 场景已渲染并检查。中文编码问题已修复。
- 正常截图退出验证没有资源泄漏警告。

截图保存在 `artifacts/`，本地日志在 `/tmp/zhanling-final-build.log` 和 `/tmp/zhanling-final-smoke.log`。

这些测试包含关卡起点定位和测试性章节切换，不等同于一次完整人工通关。未验证 Windows、Linux 或导出的独立应用。

## 2026-09-10 角色重设计

- 内置图像生成工具完成五张 1254 × 1254 RGBA 角色图集，原图及完整提示词保存在 `game/assets/characters/redesign/`。
- 65 个新角色帧资源与图集区域配置校验通过；没有重采样或改写原图像素。
- `python3 tools/build.py` 构建、规则测试、Godot 资源导入通过，无错误或警告。
- 引擎集成检查共 45 项通过，新增全部 65 个角色帧确实加载新图集且包含透明图像的检查。
- 标题、普通关卡、老人关卡与 Boss 场景已在真实 Godot 渲染器中截图并检查。
- 五类角色的待机、攻击、突进预览检查通过；修复六帧取图区域混入相邻姿势的问题。
- 在真实游戏窗口中触发挥刀并暂停查看，角色和斩击特效正常。
- 本次日志：`artifacts/character-build.log`、`artifacts/character-smoke.log`；预览：`artifacts/characters-lineup.png` 与 `artifacts/characters-*.png`。
