# 桌宠惯性物理运动实现说明（可复用指南）

本指南整理了项目中“松开后的初速度计算方式”“落地阈值”等与惯性物理相关的参数与实现细节，旨在帮助你在其他项目中复现同样的带惯性的物理运动效果。

适用对象：需要在 2D 平面上模拟带重力/摩擦/限速/边界的物体运动，支持拖拽释放后“按最后速度继续运动（抛掷效果）”，并具备“下落/落地一次”状态的 UI/游戏场景。

---

## 1. 单位体系
- 坐标/尺寸：px
- 速度：px/s
- 加速度：px/s^2
- 时间步长 Δt：s（秒）

保持单位统一是获得稳定结果的前提。

---

## 2. 关键配置项与默认值（本项目）
这些配置在启动时写入物理引擎：
- 重力加速度 gravity：`physic_gravity_acc = 800.0`
- 空气阻力加速度 airFriction：`physic_air_friction_acc = 100.0`
- 地面静摩擦加速度 staticFriction：`physic_static_friction_acc = 500.0`
- 水平速度上限 limitX：`physic_speed_limit_x = 1000.0`
- 垂直速度上限 limitY：`physic_speed_limit_y = 1000.0`
- 水平弹性系数 resilience：默认 `0`（如需反弹可设 0.2~0.6 试验）
- 落地阈值 droppedThreshold：`10.0 px`（Const 中常量）

参数来源：
- assets/ArkPetsConfigDefault.json
- core/src/cn/harryh/arkpets/ArkPets.java（将配置注入 Plane）
- core/src/cn/harryh/arkpets/Const.java（droppedThreshold）

---

## 3. 松开后的初速度计算（惯性来源）
拖拽时每一帧使用“强制改位”并按 Δx/Δt、Δy/Δt 计算即时速度：

```
// 拖拽帧：
newX = windowPos.x + mouseDeltaX
newY = windowPos.y + mouseDeltaY
if (dt > 0):
    vx = (newX - x) / dt
    vy = (newY - y) / dt
(x, y) = clampToWorld(newX, newY)
```

当松开鼠标时，不清零速度，物体以“最后一次拖动的速度”继续运动，即实现了“抛掷后带惯性”的效果。

（在原项目中对应：ArkPets.onMouseDrag → Plane.changePosition；changePosition 内部根据位移/Δt设置 speed）

---

## 4. 每帧物理更新（未拖拽时）
释放后，每帧对速度与位置进行更新（积分）：

1) 更新速度 updateVelocity(dt)
- 重力：`vy -= gravity * dt`
- 触地/触顶约束：在地面或顶边时清零对应方向速度，防穿透
- 地面静摩擦（仅触地时作用于 vx）：线性衰减至 0
- 空气阻力（作用于 vx、vy）：线性衰减至 0
- 速度限幅：`|vx| ≤ limitX`、`|vy| ≤ limitY`
- 水平弹性（可选）：若撞到左右边界且 `resilience > 0`，`vx = sqrt(vx^2 * resilience) * sign(-vx)`
- （可选）同类窗口排斥：按点电荷模型给 vx、vy 叠加 Δv，避免同类重叠（不需要可忽略）

2) 位置积分与边界限制 updatePosition(dt)
- `x += vx * dt`，`y += vy * dt`
- 对 x、y 分别做世界边界与障碍（地面条带）clamp
- 落地检测：从高于阈值的位置落到底部时，标记“落地一次”（dropped = true）并清零 vy

（在原项目中对应：ArkPets.render 非拖拽分支调用 Plane.updatePosition；内部先 updateVelocity 再积分）

---

## 5. 边界、地面与“落地一次”事件
- 世界边界 world：由一个或多个矩形区域定义（支持多显示器）。根据物体尺寸与当前坐标，得到上下左右边界。
- 一维障碍 barriers：作为“地面”条带，可承托物体。若物体在其上方并重叠 x 范围，则其顶边可作为有效地面。
- 下落/落地判定：
  - 下落中 dropping：`abs(y - borderBottom()) > droppedThreshold`
  - 落地一次 dropped：从阈值高度以上落到地面时置 true 一次（读取后即复位），便于触发一次性“落地动画”或事件。

---

## 6. 复用用法（伪代码）

```pseudo
state:
  x, y           // 位置(px)
  vx, vy         // 速度(px/s)
  w, h           // 物体尺寸(px)
  worldRects[]   // 世界矩形
  barriers[]     // 地面条带
params:
  gravity, airFriction, staticFriction
  limitX, limitY, resilience
  droppedThreshold

// 拖拽帧：
function onDrag(dt, mouseDX, mouseDY):
  newX = x + mouseDX
  newY = y + mouseDY
  if dt > 0:
    vx = (newX - x) / dt
    vy = (newY - y) / dt
  (x, y) = clampToWorld(newX, newY)

// 松开后每帧：
function update(dt):
  // 速度更新
  vy -= gravity * dt
  if onGround(): vy = 0
  if touchingTop() and vy > 0: vy = 0

  if onGround(): vx = approachZero(vx, staticFriction * dt)
  vx = approachZero(vx, airFriction * dt)
  vy = approachZero(vy, airFriction * dt)

  vx = clampAbs(vx, limitX)
  vy = clampAbs(vy, limitY)

  if atLeftOrRightBorder() and resilience > 0:
    vx = sqrt(vx*vx * resilience) * sign(-vx)

  // 位置积分与限制
  x = clampX(x + vx * dt)
  y = clampY(y + vy * dt)

  // 落地检测（一次性事件）
  if justLandedFromHigherThan(droppedThreshold):
    dropped = true
    vy = 0
```

辅助函数：
- `approachZero(v, d)`: 线性向 0 收敛，若 `sign(v)*d` 会越过 0，则直接置 0
- `clampAbs(v, L)`: 将 v 限制在 `[-L, L]`
- `clampX/clampY`: 考虑世界矩形与条带障碍后的限制
- `onGround()`: y 位于底边或障碍顶边

---

## 7. 参数调优建议
- 拖拽抛掷感：由最后一次拖拽速度决定。提高帧率与准确 dt 能获得更真实的初速度。
- 阻尼感觉：空气阻力越大，速度越快衰减；静摩擦越大，落地后的水平滑行越短。
- “轻盈/厚重”感：减小重力或增大空气阻力更“轻盈”，相反更“厚重”。
- 落地阈值：根据 UI 尺寸与期望动画触发敏感度微调（默认 10px）。
- 弹性：默认 0，若需要“碰壁反弹”，可设 0.2~0.6 之间试验。

---

## 8. 在你的项目中落地的步骤
1) 复制物理核心：位置/速度状态、updateVelocity 与 updatePosition 思路。
2) 在拖拽帧按 Δx/Δt 计算初速度，松开时不清零速度。
3) 配置重力、摩擦、限速、边界（单/多矩形）、地面条带（可选）。
4) 每帧执行“速度更新 → 位置积分 → 边界/障碍限制 → 落地判定”。
5) 若需要动画联动：
   - 下落中（dropping=true）可不切换动画或播放“空中/下落”待机。
   - 刚落地（dropped=true）触发一次性“落地反应”。

---

## 9. 本项目中的对应实现（便于对照）
- 物理引擎：core/src/cn/harryh/arkpets/utils/Plane.java
- 主循环与拖拽释放：core/src/cn/harryh/arkpets/ArkPets.java
- 默认配置：assets/ArkPetsConfigDefault.json
- 落地阈值常量：core/src/cn/harryh/arkpets/Const.java

如需最小可运行示例类，我可以按本说明抽取一个独立类文件，便于你拷贝到新项目直接使用。

---

## 10. 参数来源与源码片段

以下为“重力、空气阻力、静摩擦、速度上限、落地阈值”等参数在项目中的直接来源代码，便于在其他项目中对照迁移。

- 默认配置（assets/ArkPetsConfigDefault.json）

```json
{
  "physic_air_friction_acc": 100.0,
  "physic_gravity_acc": 800.0,
  "physic_speed_limit_x": 1000.0,
  "physic_speed_limit_y": 1000.0,
  "physic_static_friction_acc": 500.0
}
```

- 配置字段定义（core/src/cn/harryh/arkpets/ArkConfig.java）

```java
public float physic_gravity_acc;
public float physic_air_friction_acc;
public float physic_static_friction_acc;
public float physic_speed_limit_x;
public float physic_speed_limit_y;
```

- 配置注入物理引擎（core/src/cn/harryh/arkpets/ArkPets.java）

```java
plane = new Plane();
plane.setGravity(config.physic_gravity_acc);
plane.setResilience(0);
plane.setFrict(config.physic_air_friction_acc, config.physic_static_friction_acc);
plane.setObjSize(cha.camera.getWidth(), cha.camera.getHeight());
plane.setSpeedLimit(config.physic_speed_limit_x, config.physic_speed_limit_y);
```

- 落地阈值常量（core/src/cn/harryh/arkpets/Const.java）

```java
public static final float droppedThreshold = 10f;
```

- 物理参数 Setter（core/src/cn/harryh/arkpets/utils/Plane.java）

```java
/** Sets the gravity acceleration. */
public void setGravity(float gravity) { /* ... */ }

/** Sets the bounce coefficient. */
public void setResilience(float resilience) { /* ... */ }

/** Sets the friction params. */
public void setFrict(float airFrict, float staticFrict) { /* ... */ }

/** Sets the size of the object. */
public void setObjSize(float objWidth, float objHeight) { /* ... */ }

/** Sets the limitation of speed, 0=unlimited. */
public void setSpeedLimit(float x, float y) { /* ... */ }
```

- 阈值使用位置（core/src/cn/harryh/arkpets/utils/Plane.java）

```java
import static cn.harryh.arkpets.Const.droppedThreshold;
// ...
if (droppedHeight >= droppedThreshold) { /* 标记落地一次 */ }
// ...
return Math.abs(position.y - borderBottom()) > droppedThreshold; // dropping 判定
```

以上源码片段与第 2 章的“关键配置项与默认值”逐一对应，可直接作为参考在你的项目中建立等价的参数输入与注入流程。