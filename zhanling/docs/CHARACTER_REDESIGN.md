# 角色重设计

已完成五类角色的绘制与游戏接入。使用内置 `image_gen` 工具生成，未使用 API / CLI。
内置工具不提供模型版本信息，因此本项目不将这些图片标记为指定的 Image 2.5 快照。

## 角色与原图

原始 PNG 保存在 `game/assets/characters/redesign/`，每张为 1254 × 1254 RGBA，
包含 16 个姿势并带真实透明通道。全部原图保留生成像素，游戏通过图集区域引用。

| 文件 | 身份与造型 |
| --- | --- |
| `ninja.png` | 影十七：青黑叠衣、遮面头巾、朱红长巾、缠臂与小腿绑带、单刃刀。 |
| `soldier.png` | 刀兵：铁灰札甲、封闭头盔、暗红腰带、厚实护肩与制式短刀。 |
| `archer.png` | 弓手：斗笠、灰蓝披风、皮革护臂、背负箭囊与长弓；攻击包括搭箭、拉弓与放箭。 |
| `magistrate.png` | 监刑使：高冠、金属面甲、绛红官袍、旧金护甲与行刑刀；保留原有 Boss 放大比例。 |
| `scribe.png` | 老人及执笔人：素色长袍、白须、卷轴、毛笔与布袋。两处剧情人物仍共用同一套皮肤。 |

## 实际提示词

五次生成使用的完整提示词分别保存于：

- `game/assets/characters/redesign/prompts/ninja.txt`
- `game/assets/characters/redesign/prompts/soldier.txt`
- `game/assets/characters/redesign/prompts/archer.txt`
- `game/assets/characters/redesign/prompts/magistrate.txt`
- `game/assets/characters/redesign/prompts/scribe.txt`

共同方向为东方雨夜、清晰墨线、手绘赛璐璐明暗、统一角色身份与比例。
每张图要求四列四行：待机两帧、跑动六帧、跳跃一帧、攻击三帧、突进及其他姿势四帧。

## 游戏接入

游戏使用 65 个 `AtlasTexture` 帧资源，保持每类角色原有的 idle 2、run 6、jump 1、
attack 3、dash 1 的动作数量和播放速度。监刑使的收刀帧选用图集最后一格，保证武器可见。

`layout.json` 记录每帧的原图区域、身体横向锚点、落脚点和逻辑画布边距。
逻辑画布为 512 × 384；绘制时保持宽高比例，角色脚底与物理原点对齐。
跳跃姿势使用同一行的地面基线，保留收腿与腾空的空间。

六个边界紧密的动作帧使用分段取图区域，避免把相邻角色的披风、刀尖或腿部带入。
分段区域保存在 `layout.json` 和 `.tres` 元数据中，由引擎直接从原 PNG 绘制，
不修改原始 PNG，不产生重复的分帧位图。

`ActorVisual::load_frame()` 统一加载资源；战斗人物、标题主角、突进残影与剧情老人
共用同一入口。`frame_rect()` 与 `draw_frame()` 统一比例、落脚点和分段取图。
旧 SVG 留作缺失资源时的备用素材，旧素材生成器不会覆盖这套 PNG。

修改图集区域或边距后执行：

```sh
python3 tools/import_character_atlases.py
python3 tools/import_character_atlases.py --check
python3 tools/build.py
```

导入工具仅使用 Python 标准库，游戏运行无需 Python。

## 验证与预览

- C++ 构建、规则测试和 Godot 资源导入。
- 65 个新角色帧在真实 Godot 引擎中加载并验证透明图像。
- 既有移动、跳跃、突进、战斗、Boss、五章流程、平台路线与箭矢反射集成测试。
- 标题、普通关卡、老人关卡与 Boss 场景的真实引擎截图。
- `artifacts/characters-lineup.png`：五类角色的待机、攻击、突进预览。
- `artifacts/character-preview.html`：开发用预览，可切换跑动循环；通过项目根目录的本地 HTTP 服务打开。

原图、运行时资源与提示词保存在项目中。开发截图和日志位于被 Git 忽略的 `artifacts/`。
