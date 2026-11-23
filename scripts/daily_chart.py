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
    ["◆ Chips to China（晶片）", "2", "15",
     "2026-11-22_晶片對華_BIS新規16nm節點\n2026-11-22_一線_Chips_to_China（深夜補入）",
     "TSMC 16/14nm 停運後續＋Samsung 審查\nBIS IFR 刊憲與 KYCC 執法 / 五國特別許可\nMegaspeed 案·司法委查 Lutnick / 中方反制"],
    ["◆ EV from China（電動車）", "1", "10",
     "2026-11-23_二線_EVfromChina_加拿大\n規劃中國車企投資路徑",
     "加中合資框架落實進展（加股權+本地夥伴）\n配額 17,000/49,000 輛 / Ford 反對賓頓廠\n韓國本週保護措施 / 美方反應"],
    ["◆ Tax the Rich（富人稅）", "0", "6",
     "2026-11-17 雷達日掃（0 新增）\n前報 2026-11-14_TaxTheRich_初輪掃描",
     "HR10846 stage 動向（再現仍 IH）\nWays & Means / Wyden / BTC 加密政治反應"],
    ["◆ AI 信貸風險", "3", "4",
     "2026-11-23_四線_參議院通過BAAJA\n數據中心電網成本法案 + 11-22_四線\n+ 11-22_CDS飆升銀行折價拋售",
     "眾議院 BAAJA：550 億條款存留？/ 遊說\nCoreWeave CDS 破 1,500bp？/ Oracle 降級\n銀行二手貸款價下沉 / Neocloud 融資條款"],
]
COL_WIDTHS = [0.16, 0.09, 0.09, 0.33, 0.33]
ROW_H = 0.135
HEAD_H = 0.09

fig_w, fig_h = 16, 6.6
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
