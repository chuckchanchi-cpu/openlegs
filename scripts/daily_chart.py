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
    ["◆ Chips to China（晶片線）", "5", "26",
     "2026-11-26_晶片線_BIS遙距存取新規生效封堵海外算力租賃\n新規生效：封堵海外算力租賃、二手晶片湧現\n（11-25 深夜補：遙距存取新規＋Megaspeed 黑名單）",
     "新規生效後續：二手 Nvidia 晶片市場消化與價格\n許可證批核（1,200 萬 TPP 門檻）/ GMI Cloud 3 億美元貸款\n東南亞數據中心衝擊 / Megaspeed 後續＋S.3301 全院排期\n80 實體 Entity List 刊憲 FR？/ 中方反制"],
    ["◆ EV from China／關稅線", "4", "17",
     "2026-11-26_關稅線_美國新一輪301關稅針對中國歐盟等14方\n新一輪 301 關稅：對華最高 20%、違約可翻倍至 40%\n（11-25 深夜補：歐盟混能車設限＋美國 301 提案）",
     "301 稅率清單細節與最早明年生效時間表\n「不守休戰」翻倍至 40% 條款 / 中方反制與談判\n歐盟混能配額 12-1 實施細節／配額用量 17,000/49,000 輛\n法國碳標準補貼效應擴散 / 加中合資框架落實進展"],
    ["◆ AI 信貸風險", "5", "13",
     "2026-11-26_AI信貸線_CDS集體創新高490億美元貸款賬簿凍結\nCDS 集體創新高＋490 億美元貸款賬簿被凍結\n（11-25 深夜補：銀行減持數據中心貸款＋Oracle CDS 急升）",
     "CoreWeave CDS 1,314bp（隱含 68% 違約）／Oracle 356bp 走勢\n490 億美元賬簿凍結後續與 GMI Cloud\nUOB 10 億美元 SRT＋銀行減持 / 評級機構降級？\nJPM 4,500 億再融資壓力"],
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
