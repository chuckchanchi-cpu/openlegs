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
    ["◆ Chips to China（晶片）", "1", "11",
     "2026-11-20_晶片_BIS新規堵截遠程算力繞道+國會披露87萬芯片放行 · 11-20_BIS新規限雲端遙距取用+國會揭露87萬芯片批核",
     "IFR 刊憲/諮詢後續 / TSMC·三星停運對華出貨 / 國會 87.9 萬批核立法反應 / 第三國轉運執法 / 中方反制"],
    ["◆ EV from China（電動車）", "1", "9",
     "2026-11-20_電動車_加拿大審視中國電動車軍事場地准入+美國施壓 · 11-19_加中貿易解凍",
     "加國軍事/政府場地審視進展 / 49,000 輛配額規則（Tesla 佔用）/ Navarro 施壓 / 2027 回扣縮減 / 英國關稅檢討"],
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
