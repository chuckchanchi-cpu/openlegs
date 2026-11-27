#!/usr/bin/env python3
# openlegs 晚報圖表：報表式表格圖（三線 × 今日新動態/累積追蹤/最新報告/聽日追蹤點）
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.table import Table
from datetime import date
import os

# 字體：PingFang HK 優先
for fam in ["PingFang HK", "Hiragino Sans GB", "Arial Unicode MS"]:
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break
plt.rcParams["axes.unicode_minus"] = False

HEADERS = ["雷達線", "今日新動態", "累積追蹤", "最新報告", "聽日追蹤點"]
ROWS = [
    ["◆ Chips to China（晶片線）", "4", "30",
     "2026-11-26_Chips-to-China_BIS新規封鎖遙距算力及東南亞數據中心\n遙距存取新規生效：東南亞數十億美元數據中心交易停擺\n（11-26 日間：新規生效封堵海外算力租賃、二手晶片湧現）",
     "遙距新規生效後續：東南亞交易停擺消化與二手晶片市場價格\n許可證批核（1,200 萬 TPP 門檻）/ GMI Cloud 3 億美元貸款\nDayOne 上市擱置 / Megaspeed 後續＋S.3301 全院排期\n80 實體 Entity List 刊憲 FR？/ BIS 50% 規則（稀土籌碼）"],
    ["◆ EV from China／關稅線", "4", "21",
     "2026-11-26_EV-from-China_美國新一輪對華關稅最高40\n新一輪關稅：中國／越南基礎 20%、最高 40%、最快明年生效\n（11-26 日間：301 關稅針對中國歐盟等 14 方）",
     "301 稅率清單細節與最早明年生效時間表\n「不守休戰」翻倍至 40% 條款 / 12 月 G20 邁阿密習特會節奏\n中方「必要措施」反制 / 歐盟混能配額 12-1 實施細節\n配額用量 17,000/49,000 輛 / 加中合資框架落實進展"],
    ["◆ AI 信貸風險", "8", "21",
     "2026-11-27_AI信貸風險_英倫銀行警告4萬億AI敞口與大行甩賣AI貸款\nBoE 首次官方量化：AI 敞口逾 4 萬億美元、系統性風險警告\n（11-26 深夜補：CDS 創新高＋晶片管制波及數據中心貸款）",
     "BoE FSR 後續：Fed／ECB 跟進？12 月 FOMC\n花旗／大摩甩賣 AI 貸款組合定價 / SRT 定價（UOB＋BBVA）\nCoreWeave CDS 1,314bp（隱含 68%）＋2031 債息 18%\nOracle 356bp、SoftBank 501bp / 490 億賬簿凍結與 GMI Cloud"],
]
COL_WIDTHS = [0.15, 0.09, 0.09, 0.335, 0.335]
ROW_H = 0.19
HEAD_H = 0.09

fig_w, fig_h = 16, 5.8
fig, ax = plt.subplots(figsize=(fig_w, fig_h))
ax.axis("off")

fig.canvas.draw()  # 觸發字體解析

title = f"openlegs 立法雷達 — 晚報報表（{date.today().isoformat()}）"
ax.set_title(title, fontsize=17, pad=14, fontweight="bold")

tbl = Table(ax, bbox=[0.02, 0.06, 0.96, 0.84])
n_cols = len(HEADERS)

# 表頭
x = 0.0
for j, head in enumerate(HEADERS):
    tbl.add_cell(0, j, COL_WIDTHS[j], HEAD_H, text=head,
                 loc="center", facecolor="#2E86AB", edgecolor="white")
    x += COL_WIDTHS[j]

# 資料行（隔行底色）
for i, row in enumerate(ROWS):
    bg = "#F5F7FA" if i % 2 == 0 else "#FFFFFF"
    for j, cell in enumerate(row):
        align = "center" if j in (1, 2) else "left"
        t = tbl.add_cell(i + 1, j, COL_WIDTHS[j], ROW_H, text=cell,
                         loc=align, facecolor=bg, edgecolor="#B0B8C4")
        t.set_fontsize(11)
        if j == 1:
            t.set_fontsize(13)
            t.set_text_props(fontweight="bold", color="#2E86AB")
        if j == 2:
            t.set_fontsize(13)
            t.set_text_props(fontweight="bold", color="#A23B72")

for j in range(n_cols):
    tbl._cells[(0, j)].set_fontsize(12)
    tbl._cells[(0, j)].set_text_props(color="white", fontweight="bold")

ax.add_table(tbl)

out_dir = os.path.expanduser("~/Desktop/openlegs/charts")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, f"{date.today().isoformat()}_晚報.png")
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
print(out)
