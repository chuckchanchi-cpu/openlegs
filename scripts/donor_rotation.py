#!/usr/bin/env python3
"""Donor-sector rotation chart.

Three normalised lines from 2026-10-27 (pre-election week) to latest close:
  R-leaning basket  (XLE 能源, SMH 半導體, XLK 科技, LMT 國防)
  D-leaning basket  (ICLN 清潔能源, TAN 太陽能, MSOS 大麻, XLV 醫療)
  S&P 500           (benchmark)

Normalised to 100 at the 2026-11-03 close (election day) so the pre-election
drift and the post-election reaction are visually separated.

Data: Yahoo Finance daily closes. Basket = equal-weighted mean of
constituent percentage moves, re-based daily.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

OUT = os.path.expanduser("~/.openclaw/workspace/state/openlegs")
FONT = "/home/fring1117/.fonts/NotoSansCJKsc-Regular.otf"
HKT = timezone(timedelta(hours=8))
START = "2026-10-20"
ELECTION = "2026-11-03"

BASKETS = {
    "R 金主籃": (["XLE", "SMH", "XLK", "LMT"], "#C0392B"),
    "D 金主籃": (["ICLN", "TAN", "MSOS", "XLV"], "#2471A3"),
}
BENCH = ("%5EGSPC", "S&P 500", "#7F8C8D")


def series(sym):
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/"
           f"{sym}?interval=1d&range=2mo")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)
    res = d["chart"]["result"][0]
    ts = res["timestamp"]
    cl = res["indicators"]["quote"][0]["close"]
    out = {}
    for t, c in zip(ts, cl):
        if c is None:
            continue
        day = datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d")
        if day >= START:
            out[day] = c
    return out


def basket_daily(syms):
    """Equal-weighted daily mean % change across constituents."""
    per = {s: series(s) for s in syms}
    days = sorted(set.intersection(*[set(v) for v in per.values()]))
    if not days:
        return {}
    level = 100.0
    out = {days[0]: 100.0}
    for i in range(1, len(days)):
        moves = []
        for s in syms:
            a, b = per[s][days[i - 1]], per[s][days[i]]
            moves.append((b / a - 1))
        level *= (1 + sum(moves) / len(moves))
        out[days[i]] = level
    return out


def rebase(s, day=ELECTION):
    keys = sorted(s)
    anchor = None
    for k in keys:
        if k <= day:
            anchor = k
    if anchor is None:
        return s
    base = s[anchor]
    return {k: v / base * 100 for k, v in s.items() if k >= anchor}


def main():
    os.makedirs(OUT, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.font_manager as fm
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    if os.path.exists(FONT):
        fm.fontManager.addfont(FONT)
        plt.rcParams["font.family"] = fm.FontProperties(fname=FONT).get_name()
    plt.rcParams["axes.unicode_minus"] = False

    lines = {}
    for label, (syms, colour) in BASKETS.items():
        lines[label] = (rebase(basket_daily(syms)), colour)
    bench = rebase(series(BENCH[0]))
    lines[BENCH[1]] = (bench, BENCH[2])

    fig, ax = plt.subplots(figsize=(9.4, 4.6), dpi=150)
    for label, (data, colour) in lines.items():
        if not data:
            continue
        xs = [datetime.strptime(k, "%Y-%m-%d") for k in sorted(data)]
        ys = [data[k] for k in sorted(data)]
        lw = 2.6 if "籃" in label else 1.6
        ax.plot(xs, ys, label=label, color=colour, linewidth=lw,
                marker="o", markersize=3, alpha=0.95)

    ax.axvline(datetime.strptime(ELECTION, "%Y-%m-%d"), color="#444",
               linestyle="--", linewidth=1.1, alpha=0.7)
    ax.axhline(100, color="#bbb", linewidth=0.9, alpha=0.7)
    ax.annotate("中期選舉\n11-03", xy=(datetime.strptime(ELECTION, "%Y-%m-%d"), 100),
                xytext=(8, 14), textcoords="offset points",
                fontsize=8.5, color="#444")

    ax.set_title("金主行業資產：選前押注 vs 選後反應（11-03 = 100）",
                 fontsize=13, pad=12)
    ax.set_ylabel("指數（選舉日 = 100）", fontsize=9.5)
    ax.grid(axis="y", alpha=0.25, linewidth=0.7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    ax.legend(fontsize=9, frameon=False, loc="upper left")

    # latest value labels
    for label, (data, colour) in lines.items():
        if not data:
            continue
        k = sorted(data)[-1]
        ax.annotate("%s %+.1f%%" % (label.split()[0], data[k] - 100),
                    xy=(datetime.strptime(k, "%Y-%m-%d"), data[k]),
                    xytext=(6, -4), textcoords="offset points",
                    fontsize=8.2, color=colour, fontweight="bold")

    fig.text(0.99, 0.015, datetime.now(HKT).strftime("%Y-%m-%d %H:%M HKT"),
             ha="right", fontsize=7, color="#999")
    fig.text(0.01, 0.015, "籃子＝成分股等權平均；資料：Yahoo Finance 日收",
             ha="left", fontsize=7, color="#999")
    fig.tight_layout()
    path = os.path.join(OUT, "donor_rotation.png")
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    for label, (data, _) in lines.items():
        if data:
            k = sorted(data)[-1]
            print("%-10s %s  %+.2f%%" % (label, k, data[k] - 100))
    print("MEDIA:%s" % path)


if __name__ == "__main__":
    main()
