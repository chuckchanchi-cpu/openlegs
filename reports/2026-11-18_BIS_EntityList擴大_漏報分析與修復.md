# BIS Entity List 擴大 + AI 晶片第三國管制 — 為何雷達漏報及修復（2026-11-18）

> 來源：BIS 官方新聞頁（bis.gov/news-updates）、Federal Register API 實測、fring1118 補充新聞事實
> 核實：本文所有 FR 數字由 API 直接取得，可重跑

## 事件本體（2026-11-16~17 美國時間）

**BIS（商務部工業安全局）發布兩項重大管制：**

1. **Entity List 擴大**：新增 80 個實體，涵蓋中國、UAE、南非、伊朗、台灣等。
   - 12 個實體（11 中國 + 1 台灣）：從事先進晶片/超算/高性能運算研發
   - 27 個中國實體：獲取美國產品支援軍事現代化（高超音速武器等）
   - 其餘涉核不擴散、導彈、無人機等
   - 商務部長 Lutnick 聯合聲明

2. **AI 晶片第三國出口管制**（interim final rule）：
   - 先進 AI 晶片出口到馬來西亞、新加坡、印尼、泰國、巴西需許可證
   - 堵「中國企業租用第三國數據中心遠端取用美國算力」漏洞
   - ByteDance 獲豁免（爭議位）
   - 中方強烈譴責

## 點解雷達完全漏報

根本原因：雷達只掃國會法案（govinfo bills.xml），呢件事係行政法規。

三個發布渠道嘅時間差：

| 渠道 | 內容 | 時間差 | 我哋有冇掃？ |
|---|---|---|---|
| BIS 新聞稿（bis.gov） | Entity List 擴大、interim rule | 即日 | ❌ 冇 |
| Federal Register | 正式法規文本 | 數日後 | ❌ 冇（只掃國會法案） |
| 國會法案（govinfo） | 需要立法才能改變嘅嘢 | 數週後 | ✅ 有掃 |

呢件事同時存在兩個問題：
1. 渠道錯 — 行政法規唔走國會，走 BIS/Federal Register
2. 時間差 — 即使加咗 FR 掃描，新聞稿已經早幾日公布，FR 文本要等

我哋嘅 radar 掃咗 3 日（11/15~17）零命中，完全正常 — 因為佢只睇到國會法案。

## Federal Register API 實測結果

```
BIS FR docs since Nov 1: 3
  2026-11-09 | Rule | Extension of Suspension of End-User Controls for Affiliates
  2026-11-06 | Notice | Agency Information Collection (×2)
```

呢次嘅 Entity List 擴大同 AI 晶片第三國管制，截至 2026-11-18 01:20 HKT 仍未入 Federal Register。
即係話：如果只加 FR 掃描，仍然會漏 — 需要同時加 BIS 新聞頁掃描。

## 修復：三通道掃描

以後 radar 必須同時掃三個來源：
1. BIS 新聞頁（bis.gov/news-updates）— 最快，即日見
2. Federal Register API — 正式文本，數日後
3. govinfo bills.xml — 國會法案，數週後（現有）

時間線認知：一個政策行動可能由新聞稿開始，數日後入 FR，數週後有國會跟進立法。只掃第三個永遠會漏。

## 對中科企嘅影響（fring1118 報告）

- 🔴 依賴美國算力嘅中科企：阿里 -5%、百度 -7%、B站 -6.8%、地平線 -5.5%
- 🟢 本土半導體反升：中證半導體 +6%、華虹 +6.4%、中芯 +3.7%（賭「轉單+自主替代」）
- 🌏 連鎖：韓股 -2.59% 失守 5,000、台股 -2.18%

## 已修復

1. radar job 加第 3 通道 — BIS 新聞頁 + FR API 掃描（fring1122 做）
2. fring1118 加主動搜尋雷達 openlegs-radar-scan — 每日 13:00 + 23:00
3. write入 radar 檔 radar/2026-11-17_Chips_BIS遠端算力新規.md

