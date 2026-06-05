# Concept Taxonomy Plan

## Current Situation

As of 2026-06-04, the vault-level page counts are:

- `00_maps`: 8
- `01_laws`: 52
- `02_concepts`: 178
- `03_quantities`: 49
- `04_experiments`: 11
- `05_mathematical_tools`: 14

The real classification problem is not the whole vault. It is that `02_concepts` has become a catch-all bucket for:

- phenomenon pages
- modeling pages
- state pages
- bridge pages
- analytical mechanics pages
- nonlinear dynamics pages
- modern physics pages

That means the next step should be a controlled split of `02_concepts`, not a broad rewrite of the whole vault.

## Recommended Strategy

### 1. Keep the current six top-level folders

Do not immediately rewrite the whole vault structure. Keep:

- `00_maps`
- `01_laws`
- `02_concepts`
- `03_quantities`
- `04_experiments`
- `05_mathematical_tools`

This preserves current tooling and avoids a large broken-link migration.

### 2. Split only `02_concepts` into second-level subfolders

Recommended target structure:

- `02_concepts/foundations`
- `02_concepts/mechanics`
- `02_concepts/waves_optics`
- `02_concepts/electromagnetism`
- `02_concepts/thermo_fluids`
- `02_concepts/modern_physics`
- `02_concepts/analytical_dynamics`

### 3. Add frontmatter classification fields

Recommended new fields for concept pages:

```yaml
domain: mechanics
cluster: motion
level: core
```

Suggested value families:

- `domain`: foundations / mechanics / waves_optics / electromagnetism / thermo_fluids / modern_physics / analytical_dynamics
- `cluster`: state / motion / force / energy / field / oscillation / flow / material / symmetry / formalism / nonlinear
- `level`: intro / core / advanced / bridge

This gives you a safe intermediate step even before any folder moves.

## Proposed `02_concepts` Split

### `02_concepts/foundations`

Use this bucket for cross-domain conceptual skeleton pages:

- 參考系
- 慣性
- 慣性參考系
- 非慣性參考系
- 伽利略變換
- 洛侖茲轉換
- 時間
- 位移
- 力
- 功
- 能量
- 動能
- 位能
- 場
- 場論觀點
- 相互作用
- 對稱性
- 守恆律
- 守恆量
- 平衡
- 穩定平衡
- 不穩定平衡
- 穩態
- 暫態
- 邊界條件

### `02_concepts/mechanics`

Use this bucket for classical mechanics, constraints, rigid-body, and rotational behavior:

- 中心力
- 圓周運動
- 張力
- 摩擦力
- 重力
- 推進
- 質心
- 剛體
- 定軸轉動運動學
- 滾動
- 滾動運動
- 衝量
- 角動量
- 角衝量
- 角動量與碰撞
- 軌道角動量
- 轉矩
- 進動
- 章動
- 陀螺
- 碰撞
- 碰撞分析
- 機械平衡
- 靜力平衡
- 有效位能
- 保守力
- 非保守力
- 耗散
- 彈性

### `02_concepts/waves_optics`

Use this bucket for oscillations, wave behavior, and optics:

- 簡諧運動
- 阻尼振動
- 受迫振動
- 共振
- 模態
- 正常模態
- 機械波
- 聲波
- 相位
- 相干性
- 駐波
- 都卜勒效應
- 干涉
- 繞射
- 單縫繞射
- 雙縫干涉
- 薄膜干涉
- 偏振
- 反射
- 折射
- 全反射
- 惠更斯原理
- 光線模型
- 解析度
- 顯微鏡

### `02_concepts/electromagnetism`

Use this bucket for fields, media, EM propagation, and circuits:

- 直流電路
- 交流電
- RC電路
- RL電路
- RLC電路
- 串聯電路
- 並聯電路
- 節點分析
- 迴路分析
- 內電阻
- 電容器
- 平行板電容器
- 變壓器
- 自感
- 互感
- 位移電流
- 位移電流修正
- 電介質
- 介電常數
- 導體
- 屏蔽效應
- 電位
- 電位能
- 電力線
- 電場
- 電場能
- 電場能量
- 電通量
- 通量
- 環流
- 磁力
- 磁場
- 均勻帶電球殼電場
- 無限平面電場
- 等位面
- 鏡像法
- 電磁場能量流
- 電磁波
- 電磁波傳播

### `02_concepts/thermo_fluids`

Use this bucket for thermodynamics, statistical ideas, and fluid behavior:

- 溫度
- 內能
- 熱
- 熱傳導
- 熱平衡
- 熱機
- 熱膨脹
- 潛熱
- 熵
- 可逆過程
- 不可逆過程
- 等溫過程
- 絕熱過程
- 卡諾循環
- 理想氣體
- 分子運動論
- 統計物理
- 理想流體近似
- 文氏管
- 層流
- 紊流
- 黏滯力

### `02_concepts/modern_physics`

Use this bucket for quantum, relativistic, and microscopic conceptual pages:

- 光電效應
- 德布羅意波
- 波函數
- 波粒二象性
- 機率振幅
- 正規化
- 可觀測量
- 本徵態
- 算符
- 穿隧
- 薛丁格方程
- 量子化
- 離散能階
- 連續譜
- 黑體輻射
- 狹義相對論
- 局域性

### `02_concepts/analytical_dynamics`

Use this bucket for variational mechanics, Hamiltonian structure, and nonlinear dynamics:

- 廣義座標
- 約束
- 自由度
- 拉格朗日力學
- 作用量
- 哈密頓量
- 相空間
- 泊松括號
- 正則變換
- 非線性系統
- 混沌
- 初始條件敏感性
- 吸引子
- 相圖
- 龐加萊截面
- 分岔

## Why This Split Works

This split is deliberately organized around how a human searches, not around abstract metadata purity.

People usually ask:

- is this mechanics or electromagnetism?
- is this optics or wave motion?
- is this thermo or fluids?
- is this analytical mechanics or nonlinear dynamics?

They usually do not ask:

- is this a concept in the philosophical sense?

That is why a single `02_concepts` bucket is now too weak.

## Recommended Migration Order

Do not move everything at once.

### Phase 1

Add `domain`, `cluster`, and `level` frontmatter to all `02_concepts` pages without moving files.

### Phase 2

Move only the most obvious pages first:

- `analytical_dynamics`
- `modern_physics`
- `thermo_fluids`

These groups have the least naming ambiguity.

### Phase 3

Move:

- `electromagnetism`
- `waves_optics`
- `mechanics`

These are larger and more interconnected, so they should come after the classification metadata is already in place.

### Phase 4

Move `foundations` last.

These pages are the most cross-linked and most likely to act as bridge pages, so they should be the final structural move, not the first.

## Recommended Companion Map Pages

To avoid relying too much on folders, add a second layer of navigation pages in `00_maps`:

- 力學核心概念圖
- 振動波動與光學概念圖
- 電磁學核心概念圖
- 熱學與流體概念圖
- 近代物理概念圖
- 分析力學與非線性動力系統圖

Each map should separate:

- skeleton concepts
- laws
- quantities
- representative phenomena
- advanced extensions

## Practical Recommendation

If you want the safest next action, do this in order:

1. add classification frontmatter to `02_concepts`
2. create the 6 secondary map pages above
3. only then start moving concept files by domain

That gets you most of the organizational gain without immediately risking a large broken-link event.
