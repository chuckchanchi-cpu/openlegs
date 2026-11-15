# openlegs — 立法雷達（Legislative Radar）

> **Repo**: https://github.com/chuckchanchi-cpu/openlegs（public，main）
> 2026-11-14 成立。發起人 Chuck，由 OpenClaw 團隊（fring1118 / fring1122-agent）協作。
> 起因：fring1122-agent 嘅 TAX LEGISLATION WATCH 隨機彈出，Chuck 決定正經做立法研究 —「from the prerequisites stage」。

## 🎯 目標

由「前置階段」開始追蹤各國立法/政策動態。**總目標：撰寫「中期選舉後民主黨權力」評估**（draft the power of democrats after the mid-term election），三線雷達提供證據：

1. **Chips to China**：美國晶片法案、出口管制（BIS rules、Entity List、SME 設備管制）
2. **EV from China**：電動車關稅（Section 301 / Section 232）、電池管制、中國反制
3. **Tax the Rich**：財富稅、buy-borrow-die、退休帳戶改革 → 民主黨議程嘅試金石

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

## 👥 分工（2026-11-14 Chuck 指定）

- **fring1122-agent**：今個月 cron job 雷達跟進（token 新充，主執行）
- **fring1118（Claw）**：supervisor — 盯進度、收結果、驗證質量
- **ai1 Claude（Opus/Ultra）**：重型研究（需要時）

## 📐 流程規約（持續更新）

1. **待補編號（2026-11-16 Chuck 核准）**：radar 檔案入面如有法案描述但未有法案編號（HR/S 號），必須標記為「待補編號」，唔好當已核實條目；fring1122-agent 負責執行檢查
2. **API key 管理**：任何 key 唔好喺公開 channel 明文發布；fring1122-agent 存喺 600 權限檔案；付費 key 建議定期 rotate
3. **呈現 lead**：fring1118 負責 dashboard/表格/晚報；fring1122-agent 數據支援；ai1 Claude 重型研究

## 📅 時間線

- 2026-11-14：成立；完成三線初輪掃描（Chips Act→China、EV→China、Tax the Rich，見 radar/）
- 2026-11-03：美國中期選舉，民主黨大勝 — 本項目嘅分析起點
