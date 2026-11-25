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
    ["◆ Chips to China（晶片）", "3", "21",
     "2026-11-25_1_Chips_to_China\nBIS 名單化執法＋新規堵截算力漏洞\n（11-24 深夜補：新規封堵雲端漏洞＋Megaspeed 黑名單）",
     "Megaspeed 列名後續＋轉運刑事調查\n遙距存取規則許可證批核（1,200 萬 TPP 門檻）\nTSMC 16/14nm 停運後續＋Samsung / S.3301 全院排期\n80 實體 Entity List 擴大刊憲 FR？/ 中方反制"],
    ["◆ EV from China（電動車）", "3", "13",
     "2026-11-25_2_EV_from_China\n美國重建全球關稅＋歐盟封堵混能缺口\n（11-24 深夜補：EU 對中國混能車實施進口配額）",
     "美國新一輪全球關稅最快本週公布（16 經濟體稅率清單＋豁免）\n歐盟混能配額 12-1 實施細節／提前用盡配額\n配額用量 17,000/49,000 輛 / 加中合資框架 / 韓國保護措施\n2027Q1 中國電芯及正極去庫存壓力"],
    ["◆ AI 信貸風險", "3", "8",
     "2026-11-25_4_AI信貸風險\nAI CDS 集體創歷史高位（觀察→警戒）\n（11-24 深夜補：ING 數據中心貸款流拍與 AI 信貸收緊）",
     "SoftBank CDS 501bp／CoreWeave 隱含 68% 違約機率走勢\n評級機構跟進降級？/ ING 同類貸款定價＋銀行收緊 AI 敞口\n下批 AI 債券定價 / 眾議院 BAAJA 審議"],
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
