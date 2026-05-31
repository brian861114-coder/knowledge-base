# 普通物理百科 Schema

這份文件定義「大學普通物理學」知識庫的頁型、固定章節、關聯規則與示範案例，目標是同時服務：

- Obsidian 內容編寫
- AI agent 結構化處理
- 前端互動式知識地圖渲染

## 1. 設計原則

### 1.1 雙重視角

- 對讀者：以物理領域導覽，例如力學、熱學、電磁學、波動與光學、近代物理
- 對系統：以頁型與關聯結構處理，例如 `law`、`concept`、`quantity`

### 1.2 一頁一職責

- `law` 頁負責定律、定理、守恆律、方程關係
- `concept` 頁負責抽象物理觀念
- `quantity` 頁負責物理量、常數、可測量量
- `experiment` 頁負責經典實驗與驗證方法
- `mathematical_tool` 頁負責數學工具
- `map` 頁負責導覽，不承載重正文

### 1.3 導覽是樹，知識是圖

- 使用者瀏覽路徑可用樹狀結構
- 物理知識本身必須允許多重交叉連結

## 2. 領域分類

第一版建議使用以下頂層領域：

- 力學
- 熱學
- 電磁學
- 波動與光學
- 近代物理

可選補充分區：

- 數學工具
- 物理常數與單位
- 實驗方法

## 3. 頁型定義

## 3.1 `law`

用途：描述物理定律、定理、守恆律、核心方程。

例子：

- 牛頓第二定律
- 庫侖定律
- 高斯定律
- 熱力學第一定律
- 理想氣體定律

建議 frontmatter：

```yaml
---
type: law
title:
domain:
summary:
applicability:
prerequisites: []
related_concepts: []
related_quantities: []
related_laws: []
experiments: []
math_tools: []
derived_results: []
modern_connections: []
tags: []
updated:
---
```

固定章節：

1. 定律摘要
2. 適用條件
3. 數學表述
4. 物理直觀
5. 歷史背景
6. 實驗驗證
7. 推導
8. 典型應用
9. 常見誤解
10. 先備知識
11. 相關概念
12. 衍生結果
13. 現代理論視角

## 3.2 `concept`

用途：描述抽象概念與物理觀念。

例子：

- 力
- 場
- 能量
- 熵
- 電位

建議 frontmatter：

```yaml
---
type: concept
title:
domain:
summary:
prerequisites: []
related_laws: []
related_quantities: []
related_concepts: []
math_tools: []
tags: []
updated:
---
```

固定章節：

1. 概念摘要
2. 基本定義
3. 物理意義
4. 直觀理解
5. 歷史背景
6. 代表性定律
7. 典型例子
8. 常見誤解
9. 先備知識
10. 相關概念
11. 現代理論視角

## 3.3 `quantity`

用途：描述物理量、常數、可測量量與其表徵。

例子：

- 速度
- 加速度
- 動量
- 壓力
- 電荷
- 電場

建議 frontmatter：

```yaml
---
type: quantity
title:
symbol:
unit:
dimension:
domain:
summary:
related_concepts: []
related_laws: []
measurement_methods: []
tags: []
updated:
---
```

固定章節：

1. 物理量摘要
2. 定義
3. 符號與單位
4. 維度與量綱
5. 幾何或物理意義
6. 量測方式
7. 出現於哪些定律
8. 典型應用
9. 常見誤解
10. 相關概念

## 3.4 `experiment`

用途：描述經典實驗、驗證方式與量測設計。

例子：

- 卡文迪西實驗
- 密立根油滴實驗
- 楊氏雙縫實驗
- 麥克耳孫-莫雷實驗

建議 frontmatter：

```yaml
---
type: experiment
title:
summary:
domain:
tested_laws: []
measured_quantities: []
related_concepts: []
historical_period:
tags: []
updated:
---
```

固定章節：

1. 實驗摘要
2. 問題背景
3. 裝置與方法
4. 可觀測量
5. 實驗結果
6. 支持或挑戰的定律
7. 誤差與限制
8. 歷史影響
9. 相關概念

## 3.5 `mathematical_tool`

用途：描述理解物理所需的數學工具。

例子：

- 向量分解
- 微分
- 積分
- 微分方程
- 梯度
- 散度
- 旋度

建議 frontmatter：

```yaml
---
type: mathematical_tool
title:
summary:
used_in: []
prerequisites: []
related_concepts: []
tags: []
updated:
---
```

固定章節：

1. 工具摘要
2. 數學定義
3. 幾何意義
4. 為什麼物理需要它
5. 在哪些主題中出現
6. 典型操作
7. 常見誤解
8. 相關工具

## 3.6 `map`

用途：作為導覽頁、學習路徑頁、知識總覽頁。

例子：

- 力學總覽
- 電磁學學習路徑
- 熱學概念地圖

建議 frontmatter：

```yaml
---
type: map
title:
summary:
focus_domain:
includes: []
recommended_order: []
tags: []
updated:
---
```

固定章節：

1. 地圖摘要
2. 範圍說明
3. 主要主題
4. 建議學習順序
5. 關鍵定律
6. 關鍵概念
7. 先備知識
8. 延伸方向

## 4. 關聯類型

第一版建議固定使用以下關聯：

- `requires`
  - A 需要先懂 B
- `defines`
  - A 定義了 B
- `uses`
  - A 使用了 B
- `derives_to`
  - A 可推導到 B
- `explains`
  - A 可解釋 B
- `verified_by`
  - A 被某實驗支持或驗證
- `measures`
  - 某實驗測量某物理量
- `formalized_by`
  - 某概念或定律依賴某數學工具
- `organized_by`
  - 某頁被某導覽頁收納
- `related_to`
  - 一般性相關連結，僅在無法更精確標示時使用

## 5. 頁型之間允許的連線

### 5.1 `law`

可連到：

- `concept`
- `quantity`
- `experiment`
- `mathematical_tool`
- `law`
- `map`

典型關係：

- `uses`
- `requires`
- `derives_to`
- `verified_by`
- `formalized_by`
- `organized_by`

### 5.2 `concept`

可連到：

- `law`
- `quantity`
- `concept`
- `mathematical_tool`
- `map`

典型關係：

- `defines`
- `related_to`
- `requires`
- `formalized_by`
- `organized_by`

### 5.3 `quantity`

可連到：

- `law`
- `concept`
- `experiment`
- `mathematical_tool`

典型關係：

- `used_in`
- `measures`
- `related_to`
- `formalized_by`

備註：`used_in` 可在實作時併入 `uses`，但顯示層可保留語意差異。

### 5.4 `experiment`

可連到：

- `law`
- `quantity`
- `concept`
- `map`

典型關係：

- `verified_by`
- `measures`
- `explains`
- `organized_by`

### 5.5 `mathematical_tool`

可連到：

- `law`
- `concept`
- `quantity`
- `mathematical_tool`

典型關係：

- `formalized_by`
- `requires`
- `related_to`

### 5.6 `map`

可連到所有頁型。

典型關係：

- `organized_by`
- `requires`
- `related_to`

## 6. 實作規則

### 6.1 Obsidian 規則

- 每頁只對應一個主要頁型
- 每頁必須有 `title` 與 `summary`
- 關聯頁面優先以 `[[wikilink]]` 表示
- frontmatter 中的陣列欄位，內容應對應實際存在的頁面

### 6.2 Agent 規則

- 先判斷頁型，再決定模板
- 不可把 `law` 頁寫成純教科書段落，必須保留結構化章節
- 不可虛構來源、歷史細節、實驗結果
- 若現代理論視角不明確，應標記為待補，不要亂補量子名詞

### 6.3 前端規則

- `summary` 用於卡片與搜尋摘要
- `requires` 可視為學習路徑邊
- `related_to` 可視為弱關聯邊
- `derives_to` 可視為推導樹邊
- `verified_by` 可視為理論到實驗的橋接邊

## 7. 示例：牛頓第二定律

以下展示 `law` 頁如何實際落地。

### 7.1 示例 frontmatter

```yaml
---
type: law
title: 牛頓第二定律
domain: 力學
summary: 物體所受合力等於其動量對時間的變化率，在質量不變時可寫為 F = ma。
applicability: 適用於經典力學範圍內的巨觀低速系統；在質量固定時可化為常見形式 F = ma。
prerequisites:
  - [[力]]
  - [[質量]]
  - [[加速度]]
  - [[向量]]
related_concepts:
  - [[慣性]]
  - [[動量]]
related_quantities:
  - [[力]]
  - [[質量]]
  - [[加速度]]
  - [[動量]]
related_laws:
  - [[牛頓第一定律]]
  - [[牛頓第三定律]]
experiments:
  - [[小車軌道實驗]]
  - [[Atwood machine]]
math_tools:
  - [[向量分解]]
  - [[微分]]
derived_results:
  - [[動量定理]]
  - [[功能定理]]
modern_connections:
  - [[拉格朗日力學]]
  - [[相對論動力學]]
tags: [mechanics, law]
updated: 2026-05-31
---
```

### 7.2 示例章節骨架

```md
# 牛頓第二定律

## 定律摘要
描述合力如何決定物體運動狀態的改變。

## 適用條件
- 經典、低速、巨觀近似
- 慣性參考系
- 常見教科書形式 F = ma 預設質量不變

## 數學表述
- 一般形式：F = dp/dt
- 質量不變時：F = ma

## 物理直觀
合力不決定速度本身，而決定速度改變的快慢與方向。

## 歷史背景
從亞里斯多德運動觀到伽利略慣性概念，再到牛頓系統化動力學。

## 實驗驗證
可用低摩擦軌道小車與已知外力驗證加速度與合力成正比。

## 推導
由動量定義與質量固定假設可得常見形式 F = ma。

## 典型應用
- 斜面運動
- 圓周運動中的向心加速度分析
- 多力平衡與非平衡問題

## 常見誤解
- 誤以為力維持速度
- 誤以為作用力與反作用力互相抵消

## 先備知識
- 向量
- 速度與加速度
- 慣性參考系

## 相關概念
- [[力]]
- [[慣性]]
- [[動量]]
- [[質量]]

## 衍生結果
- [[動量定理]]
- [[功能定理]]

## 現代理論視角
在相對論中，動量與力的關係仍保留更一般形式 F = dp/dt，但 F = ma 需小心詮釋。
```

## 8. 第一版建置順序

建議依下列順序實作：

1. 先完成 `law` 模板與 5 到 10 個代表性條目
2. 補 `concept` 與 `quantity` 頁，支撐 `law` 頁的連結
3. 為代表性定律補 `experiment` 頁
4. 為電磁學與進階力學補 `mathematical_tool` 頁
5. 最後建立 `map` 頁，組成導覽與學習路徑

## 9. 第一批建議條目

若以普通物理為起點，第一批適合建立：

- 牛頓第一定律
- 牛頓第二定律
- 牛頓第三定律
- 萬有引力定律
- 功能定理
- 動量守恆
- 理想氣體定律
- 熱力學第一定律
- 庫侖定律
- 高斯定律

配套概念與物理量：

- 力
- 質量
- 加速度
- 動量
- 能量
- 壓力
- 溫度
- 電荷
- 電場
- 電位
