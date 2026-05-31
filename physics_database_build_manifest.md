# 普通物理資料庫建置清單

這份文件把目前確定的 scope 轉成可執行的資料庫建置計畫，服務兩個目標：

- 在 Obsidian 中建立可維護的普通物理百科
- 讓前端互動式知識地圖有穩定的資料來源

## 1. 目標路徑

實際 Obsidian 頁面輸出目標：

`C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database`

工具、schema、script、前端原型仍留在目前 workspace：

`C:\Users\brian\Downloads\vibe_coding\knowledge_map`

## 2. 目錄結構

建議使用系統導向的頁型目錄，而不是直接按學科分類存放：

```text
knowledge database/
  00_maps/
  01_laws/
  02_concepts/
  03_quantities/
  04_experiments/
  05_mathematical_tools/
```

讀者導覽由 `00_maps` 下的總覽頁承擔。

## 3. 頂層領域

第一版頂層導覽頁共 8 個：

1. 數學工具總覽
2. 力學總覽
3. 振動與波動總覽
4. 熱學與熱力學總覽
5. 電磁學總覽
6. 光學總覽
7. 近代物理總覽
8. 流體力學總覽

## 4. Scope 清單

## 4.1 數學工具

- 向量：向量加法、內積、外積、單位向量
- 微積分：導數、積分、偏導數、全微分
- 常微分方程：簡諧運動、阻尼運動、RC 電路
- 多變數微積分：梯度、散度、旋度
- 線積分與面積分：電場、磁場、功、通量
- 三角函數：波動、圓周運動、相位
- 複數：交流電、波動、量子力學入門
- 矩陣與線性代數：轉動、慣性張量、偏振、量子態
- 機率與統計：熱力學、統計物理、測量誤差

## 4.2 力學

- 運動學
- 牛頓力學
- 功與能量
- 動量與碰撞
- 轉動力學
- 萬有引力

## 4.3 振動與波動

- 振動
- 波動
- 聲學

## 4.4 熱學與熱力學

- 溫度與熱
- 氣體動力論
- 熱力學定律
- 熱傳

## 4.5 電磁學

- 靜電學
- 電容與介電質
- 電流與直流電路
- 磁學
- 電磁感應
- 交流電與電磁波

## 4.6 光學

- 幾何光學
- 波動光學

## 4.7 近代物理

- 相對論
- 量子物理入門
- 原子物理
- 核物理與粒子物理入門

## 4.8 流體力學

- 密度、壓力、靜水壓
- 帕斯卡原理、浮力、阿基米德原理
- 流量、連續方程、伯努力方程
- 黏滯性、層流與亂流、雷諾數
- 表面張力、毛細現象

## 5. 第一批實作頁面

第一批不追求完整，而是先把資料庫骨架與關聯網跑起來。

### 已規劃生成的總覽頁

- `00_maps/數學工具總覽.md`
- `00_maps/力學總覽.md`
- `00_maps/振動與波動總覽.md`
- `00_maps/熱學與熱力學總覽.md`
- `00_maps/電磁學總覽.md`
- `00_maps/光學總覽.md`
- `00_maps/近代物理總覽.md`
- `00_maps/流體力學總覽.md`

### 已規劃生成的數學工具頁

- `05_mathematical_tools/向量.md`
- `05_mathematical_tools/導數.md`
- `05_mathematical_tools/積分.md`
- `05_mathematical_tools/三角函數.md`
- `05_mathematical_tools/複數.md`

### 已規劃生成的物理核心頁

- `01_laws/牛頓第二定律.md`
- `01_laws/功能定理.md`
- `01_laws/動量守恆.md`
- `01_laws/庫侖定律.md`
- `01_laws/熱力學第一定律.md`
- `01_laws/折射定律.md`
- `01_laws/伯努力方程.md`
- `02_concepts/力.md`
- `02_concepts/溫度.md`
- `02_concepts/電場.md`
- `02_concepts/機械波.md`
- `03_quantities/質量.md`
- `03_quantities/加速度.md`
- `03_quantities/動量.md`
- `03_quantities/電荷.md`

## 6. 第二批優先頁面

第二批優先補足第一批會大量連到但尚未細寫的節點：

- 牛頓第一定律
- 牛頓第三定律
- 功
- 動能
- 位能
- 簡諧運動
- 電位
- 高斯定律
- 理想氣體方程式
- 光電效應

## 7. 內容原則

- 所有頁面使用 Obsidian frontmatter 與 `[[wikilinks]]`
- `law` 頁固定使用 13 個百科章節
- `mathematical_tool` 頁強調「在物理中拿來做什麼」
- `map` 頁用來承接未完成條目，允許先有導覽後補細節
- 若某主題尚未獨立成頁，可先在總覽頁以清單與 future link 表示

## 8. 執行方式

本 workspace 內的生成腳本：

`tools/generate_physics_seed_notes.py`

預設用途：

- 建立目錄骨架
- 輸出第一批頁面到指定 Obsidian 資料庫
- 保持頁型 frontmatter 與 section 順序一致

## 9. 驗收標準

第一批完成後，至少應滿足：

1. 目標資料夾存在 8 個總覽頁
2. 至少 12 個以上核心百科頁已生成
3. 每頁有有效 frontmatter
4. 每頁有固定章節
5. 關鍵頁面之間已有 `[[wikilinks]]`
6. 前端之後可直接對這批頁面跑 graph export
