# openlegs — 立法雷達（Legislative Radar）

> 2026-11-14 成立。發起人 Chuck，由 OpenClaw 團隊（fring1118 / fring1122-agent）協作。
> 起因：fring1122-agent 嘅 TAX LEGISLATION WATCH 隨機彈出，Chuck 決定正經做立法研究 —「from the prerequisites stage」。

## 🎯 目標

由「前置階段」開始追蹤各國立法/政策動態，重點雷達：

1. **Chips Act → China**：美國晶片法案、出口管制（BIS rules、Entity List、SME 設備管制）
2. **EV → China**：電動車關稅（Section 301 / Section 232）、電池管制、中國反制

逐步擴展到：地緣經濟立法、制裁、補貼戰、供應鏈法案。

## 📁 結構

```
openlegs/
├── README.md          ← 你喺度（章領 + 進度）
├── radar/             ← 每輪掃描報告（YYYY-MM-DD_主題_內容.md）
├── reports/           ← 深度研究報告
├── scripts/           ← 雷達腳本（GovInfo API、RSS、搜索）
├── data/              ← 結構化數據（法案列表、時間線）
└── raw/               ← 原始資料（PDF、HTML 存檔）
```

## 📡 雷達機制（規劃中）

- **來源**：GovInfo API、Congress.gov、Federal Register、BIS 公告、USTR 公告
- **觸發**：新法案/新規則/新關稅變動 → 寫入 `radar/` + 通知 #general（或專用 channel）
- **現有基礎**：fring1122-agent 嘅 TAX LEGISLATION WATCH 可改造成篩選式雷達（只推 CHIPS/EV/對華關鍵詞）

## 📅 時間線

- 2026-11-14：成立；完成 Chips Act→China 同 EV→China 初輪掃描（見 radar/）
