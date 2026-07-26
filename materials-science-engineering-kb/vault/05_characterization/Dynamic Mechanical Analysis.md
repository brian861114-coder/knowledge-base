---
title: 動態機械分析
type: mathematical_tool
summary: 動態機械分析以小振幅週期載入量測材料的儲能、損耗與黏彈性轉變，特別適合判讀聚合物和其他時間依賴材料的溫度與頻率響應。
domain: Characterization
taxonomy_domain: characterization
tags: [dma]
related_concepts: [[[Viscoelastic Response|黏彈性響應]], [[Glass Transition and Thermal Transitions|玻璃轉移與熱轉變]], [[Polymers|聚合物]], [[Biomaterials|生物材料]], [[Mechanical Testing|機械試驗]]]
measured_quantities: [[[Viscoelastic Response|黏彈性響應]], [[Glass Transition and Thermal Transitions|玻璃轉移與熱轉變]], [[Mechanical Properties|機械性質]]]
---
## 為什麼這很重要

如果材料的剛度和阻尼會隨時間、溫度或頻率變化，那麼只做一次靜態力學試驗通常不夠。DMA 的價值就在於它能把儲能能力、耗能能力和轉變區間拆開來看，而不是把這些行為壓成一個粗糙的單一模數。

## 它測量什麼

DMA 在受控溫度、頻率或時間條件下施加小振幅振盪變形，並量測應力與應變之間的相位差。常見輸出包括儲能模數、損耗模數與損耗因子。這些量對應到材料中可逆彈性能量儲存、內部耗散以及黏彈性鬆弛的強弱。

## 它最擅長回答哪些問題

對聚合物、黏著層、薄膜、複材基體和軟材料而言，DMA 特別適合辨識玻璃轉移、次級鬆弛、交聯效果、濕度影響與頻率敏感性。當你想知道材料在不同使用條件下會不會突然變軟、阻尼是否足夠、或結構鬆弛是否已經發生時，DMA 通常比單純拉伸更誠實。

## 判讀重點

Tg 在 DMA 中常表現為模數快速下降區與損耗峰附近，但不同判據得到的溫度不一定相同。峰值位置、峰寬與高度都可能受到加熱速率、頻率、樣品幾何、含水量和熱歷史影響。看到一個漂亮的 tan delta 峰不代表事情就結束了，先問它對應的是哪一種鬆弛、在什麼條件下量到，以及是否與 [[Differential Scanning Calorimetry|差示掃描量熱]] 或其他結構資訊一致。

## 常見限制

DMA 主要量的是小變形下的線性或近線性響應，不能直接取代大應變破壞試驗。夾具模式、樣品尺寸、邊界條件和校正品質都會影響結果，尤其是薄膜、泡棉或非常軟的材料。若量測條件選得亂，得到的不是精細材料資訊，而只是夾具和樣品一起亂晃的數字。

## 和其他方法如何互補

DMA 與 [[Mechanical Testing|機械試驗]]、[[Differential Scanning Calorimetry|差示掃描量熱]] 和 [[Thermogravimetric Analysis|熱重分析]] 互補性很強。DSC 告訴你熱事件是否存在，DMA 則更敏感地揭露力學鬆弛與使用溫度窗口；TGA 則可協助排除揮發、分解或含水量變化對響應的干擾。把它們結合起來，才能比較像是在理解材料，而不是只是在看儀器曲線。
