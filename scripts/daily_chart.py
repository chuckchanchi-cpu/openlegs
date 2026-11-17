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
    ["◆ Chips to China（晶片）", "0", "5",
     "2026-11-17 雷達日掃（0 新增）· 前報 2026-11-14_晶片_法律工具與失效模式",
     "BIS 規則補 FR 編號 / SME 禁令立法化 / H200 / 待證動態補來源"],
    ["◆ EV from China（電動車）", "0", "5",
     "2026-11-17 雷達日掃（0 新增）· 前報 2026-11-14_EV_關稅結構與繞道機制",
     "產地規則堵漏 / BYD 墨西哥工廠 / 中方反制"],
    ["◆ Tax the Rich（富人稅）", "0", "6",
     "2026-11-17 雷達日掃（0 新增）· 前報 2026-11-14_TaxTheRich_初輪掃描",
     "HR10846 stage 動向（再現仍 IH）/ Ways & Means / Wyden / BTC 加密政治反應"],
]
COL_WIDTHS = [0.17, 0.10, 0.09, 0.32, 0.32]
ROW_H = 0.135
HEAD_H = 0.09

fig_w, fig_h = 16, 5.2
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
