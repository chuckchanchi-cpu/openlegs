#!/usr/bin/env python3
# openlegs 晚報圖表：報表式表格圖（四線 × 今日新動態/累積追蹤/最新報告/聽日追蹤點）
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
    ["◆ Chips to China（晶片）", "3", "18",
     "2026-11-24_BIS將Megaspeed列入實體清單\n2026-11-24_雷達日掃（S.3301 RS 刊憲\n+ 91 FR 74970 刊憲生效）",
     "80 實體 Entity List 擴大刊憲 FR？（待補編號）\nMegaspeed 列名後續＋轉運調查 / S.3301 全院排期\n91 FR 74970 執法落地（五國許可＋美企月報）\nTSMC 16/14nm 停運後續＋Samsung / 中方反制"],
    ["◆ EV from China（電動車）", "0", "10",
     "2026-11-23_二線_EVfromChina_加拿大\n規劃中國車企投資路徑",
     "加中合資框架落實進展（加股權+本地夥伴）\n配額 17,000/49,000 輛 / Ford 反對賓頓廠\n韓國本週保護措施 / 美方反應"],
    ["◆ Tax the Rich（富人稅）", "0", "6",
     "2026-11-17 雷達日掃（0 新增）\n前報 2026-11-14_TaxTheRich_初輪掃描",
     "HR10846 stage 動向（再現仍 IH）\nWays & Means / Wyden / BTC 加密政治反應"],
    ["◆ AI 信貸風險", "1", "5",
     "2026-11-24_CDS隱含違約機率急升\nNvidia 多線調查",
     "CoreWeave CDS 1,090bp／隱含 CCC- 61% 違約機率\nOracle 隱含 23%→評級跟進降級？/ 下批 AI 債券定價\nNvidia DOJ・SEC・國會調查＋Hugging Face 反壟斷\n眾議院 BAAJA 審議"],
]
COL_WIDTHS = [0.16, 0.09, 0.09, 0.33, 0.33]
ROW_H = 0.15
HEAD_H = 0.09

fig_w, fig_h = 16, 7.2
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
