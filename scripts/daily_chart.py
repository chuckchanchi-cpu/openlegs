#!/usr/bin/env python3
# openlegs 晚報圖表：三線雷達狀態（橫向 bar chart）
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from datetime import date
import os

# 中文字體（避免豆腐字）
for fam in ["PingFang HK", "Hiragino Sans GB", "Arial Unicode MS"]:
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break
plt.rcParams["axes.unicode_minus"] = False

lines = ["Chips to China\n(晶片法案/出口管制)", "EV from China\n(電動車關稅)", "Tax the Rich\n(財富稅/加稅議程)"]
today_new = [4, 3, 5]      # 今日新動態數（今日初輪掃描入面新記錄嘅 2026 動態）
tracking  = [5, 5, 5]      # 累積追蹤項目數（追蹤要點清單）

y = range(len(lines))
h = 0.35
fig, ax = plt.subplots(figsize=(10, 5.5))

b1 = ax.barh([i + h/2 for i in y], today_new, height=h, label="今日新動態數", color="#2E86AB")
b2 = ax.barh([i - h/2 for i in y], tracking,  height=h, label="累積追蹤項目數", color="#A23B72")

for bars in (b1, b2):
    ax.bar_label(bars, padding=4, fontsize=11)

ax.set_yticks(list(y))
ax.set_yticklabels(lines, fontsize=11)
ax.invert_yaxis()
ax.set_xlabel("項目數", fontsize=11)
ax.set_title("openlegs 立法雷達 — 三線雷達狀態（2026-11-14 晚報）", fontsize=15, pad=12)
ax.legend(loc="lower right", fontsize=11)
ax.set_xlim(0, max(today_new + tracking) + 1.5)
ax.grid(axis="x", linestyle=":", alpha=0.5)
ax.spines[["top", "right"]].set_visible(False)

out_dir = os.path.expanduser("~/Desktop/openlegs/charts")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, f"{date.today().isoformat()}_晚報.png")
fig.tight_layout()
fig.savefig(out, dpi=150)
print(out)
