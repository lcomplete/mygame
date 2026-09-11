# 野蛮人模型与动画工作流

更新：2026-09-11。

`tools/build_barbarian.py` 是 Blender 构建入口；`build_world.py` 不会覆盖野蛮人。人体、装备、动画分成三个作者文件，输出可编辑的 `art/barbarian.blend` 和游戏使用的 `game/assets/models/barbarian.glb`。

## 人体和装备

1. 使用 CC0 MakeHuman 连续人体、UV、体型目标、163 根原始骨骼和蒙皮权重，调整胸背、肩颈、脸部与肌肉轮廓。
2. **先细分人体，再拟合装备。** `barbarian_equipment.py` 在最终人体表面建立三角形 BVH，通过重心坐标转移蒙皮权重。低精度控制网格不再用于背带、战纹和护肩定位。
3. 两条肩带分层叠放，并有肩部桥接与背面连接；肩部软皮甲、包边和铆钉继承相同的肩部权重，抬臂时共同形变。
4. 裙片有 16 根附加骨骼，受大腿方向和动作影响。腰带、扣件、腰包跟随骨盆。靴子使用封闭鞋楦，脚尖和脚掌不再复制人体脚趾轮廓；脚踝区域混合小腿和足部权重。
5. 武器沿闭合手指的握持轴建模，整把武器使用对应手腕权重。指节屈曲参数与动画共用。皮革、金属和布料的颜色纹理随 GLB 导出。

## 动作与游戏时序

`barbarian_animation.py` 生成 Idle、Run、Attack、Whirlwind、Rally、WarCry、Berserk、Leap、Hit、Death 十段动作。

- 每秒 60 个采样，四元数统一符号，线性插值避免曲线过冲。
- 跑步和普通站立使用两段腿部 IK；脚踝角度连续变化。Idle、Run、Whirlwind 的首尾根位移和旋转闭合。
- 根骨骼位移显式转换到骨骼坐标，避免把局部 Z 错当成世界竖直方向。
- `game/data/barbarian_animation.json` 保存导出时长和命中事件。普通攻击在动作的 49% 处命中；腾空斩在 0.18 秒起跳、0.78 秒落地，约 1.067 秒恢复结束。
- Godot 按显示帧推进骨骼动画，角色位移开启物理插值。跑步播放速度随实际水平速度变化；攻击、呐喊、落地恢复保留各自动作时长。
- 新技能清除未完成的突进；死亡取消引导；同一技能重新施放会从蓄力帧开始。

## 验证

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python-exit-code 1 --python tools/build_barbarian.py
python3 tools/verify.py
python3 tools/verify_barbarian.py --captures
```

`verify_barbarian.py` 直接解析最终 GLB，检查 179 根骨骼、十段动作、有限变换值、蒙皮归一化、骨骼索引、动作时长、相邻旋转变化和循环接缝。`verify.py` 执行真实场景中的寻路、NPC 对话、六技能、起跳蓄力、落地恢复、资源消耗、暂停和死亡测试。

F7 打开 `hero_review.tscn`，同时查看正面、斜侧和背面。左右键切换动作、空格暂停、S 切换四分之一速；Esc 重新进入营地。该场景使用游戏 GLB；腾空展示为缩短高度的原地检查，实战仍使用完整位移和 3 米跳跃弧线。

质量检查不能证明与《暗黑2：重制版》完全一致，也不能替代每种连续操作下的穿模检查。当前为程序化重新建模版本；原版的高模雕刻、精细贴图与动作打磨并未等同复现。
