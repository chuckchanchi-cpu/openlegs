#!/usr/bin/env python3
"""openlegs dashboard — table-style PNG for easy review.

Renders a scannable table: one row per tracked item, grouped by the three
tracks. Status comes from the checklist state in radar/*.md plus recent
commit activity. No invented numbers.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta

REPO = os.path.expanduser("~/.openclaw/workspace/openlegs-repo")
OUT = os.path.expanduser("~/.openclaw/workspace/state/openlegs")
HKT = timezone(timedelta(hours=8))
FONT = "/home/fring1117/.fonts/NotoSansCJKsc-Regular.otf"

TRACKS = [
    ("晶片 → 中國", "Chip", "#4C72B0", ("chip", "semi", "晶片")),
    ("電動車 → 中國", "EV", "#DD8452", ("ev", "電動")),
    ("富人稅", "Tax", "#55A868", ("tax", "富人")),
]


def sh(cmd, cwd=None, timeout=25):
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                              timeout=timeout).stdout.strip()
    except Exception:
        return ""


def run_gatekeeper():
    """Verify bill citations first. Returns {billref: (verdict, note)} + summary."""
    script = os.path.expanduser("~/.openclaw/workspace/scripts/gatekeeper.py")
    if not os.path.exists(script):
        return {}, None
    try:
        subprocess.run([sys.executable, script], capture_output=True,
                       text=True, timeout=180)
    except Exception as e:
        print("[warn] gatekeeper failed: %s" % e, file=sys.stderr)
        return {}, None
    path = os.path.join(OUT, "gatekeeper.json")
    try:
        with open(path) as f:
            payload = json.load(f)
    except Exception:
        return {}, None

    marks = {}
    for r in payload.get("results", []):
        key = "%s%s" % (r.get("type", "").upper(), r.get("number", ""))
        verdict = r.get("match", "?")
        marks[key] = (verdict, r.get("actual_title") or "")
    summary = {"checked": payload.get("checked", 0),
               "blocked": payload.get("blocked", 0)}
    return marks, summary


def verdict_for(text, marks):
    """Find a bill reference inside an item and return its verification mark."""
    if not marks:
        return "—"
    for key, (verdict, _actual) in marks.items():
        m = re.match(r"(HR|HRES|S|SRES)(\d+)$", key)
        if not m:
            continue
        num = m.group(2)
        if re.search(r"\b%s\s*\.?\s*%s\b" % (m.group(1)[0], num), text, re.I):
            if verdict in ("EXACT", "CLOSE"):
                return "✓ 已核實"
            if verdict == "MISMATCH":
                return "✗ 標題不符"
            return "? 未證"
    return "—"


def collect():
    """Return {track_label: [(item_text, done_bool), ...]}"""
    data = {t[0]: [] for t in TRACKS}
    radar = os.path.join(REPO, "radar")
    if not os.path.isdir(radar):
        return data

    for fn in sorted(os.listdir(radar)):
        if not fn.endswith(".md"):
            continue
        low = fn.lower()
        target = None
        for label, _short, _c, keys in TRACKS:
            if any(k in low for k in keys):
                target = label
                break
        if not target:
            continue
        try:
            body = open(os.path.join(radar, fn), encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        for line in body.splitlines():
            m = re.match(r"^\s*-\s*\[([ xX])\]\s*(.+)$", line)
            if m:
                txt = re.sub(r"\s+", " ", m.group(2)).strip()
                txt = re.sub(r"[（(]關鍵詞[^）)]*[）)]", "", txt).strip()
                data[target].append((txt[:62], m.group(1).lower() == "x"))
    return data


def recent_commits(n=3):
    out = sh(["git", "log", "-%d" % n, "--format=%ad %s", "--date=format:%m-%d"], cwd=REPO)
    return [l for l in out.splitlines() if l.strip()][:n]


def render(data, commits, path, marks=None, gk=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.font_manager as fm
    import matplotlib.pyplot as plt

    if os.path.exists(FONT):
        fm.fontManager.addfont(FONT)
        fp = fm.FontProperties(fname=FONT)
        plt.rcParams["font.family"] = fp.get_name()
    plt.rcParams["axes.unicode_minus"] = False

    rows = []
    for label, short, colour, _ in TRACKS:
        items = data.get(label, [])
        if not items:
            rows.append((short, "(no items)", "—", "—", colour))
            continue
        for i, (txt, done) in enumerate(items):
            v = verdict_for(txt, marks)
            rows.append((short if i == 0 else "", txt,
                         "done" if done else "open", v, colour))

    fig_h = 0.42 * len(rows) + 1.75
    fig, ax = plt.subplots(figsize=(12.2, fig_h), dpi=150)
    ax.axis("off")

    fig.text(0.012, 0.970, "openlegs 追蹤儀表板", fontsize=17, fontweight="bold", va="top")
    subtitle = datetime.now(HKT).strftime("%Y-%m-%d %H:%M HKT") + \
        "   ·   github.com/chuckchanchi-cpu/openlegs"
    if gk:
        subtitle += "   ·   核實 %d 條引用，%d 條待處理" % (gk["checked"], gk["blocked"])
    fig.text(0.012, 0.925, subtitle, fontsize=8.6, color="#666", va="top")

    tbl = ax.table(
        cellText=[list(r[:4]) for r in rows],
        colLabels=["線", "追蹤項目", "狀態", "法案核實"],
        colWidths=[0.075, 0.655, 0.10, 0.17],
        cellLoc="left",
        bbox=[0.012, 0.125, 0.976, 0.755],
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.8)

    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("#dddddd")
        cell.set_linewidth(0.6)
        if r == 0:
            cell.set_facecolor("#23303f")
            cell.set_text_props(color="white", fontweight="bold", fontsize=9.2)
        else:
            cell.set_facecolor("#ffffff" if r % 2 else "#f7f9fb")
            if c == 2:
                cell.set_text_props(color="#1f7a3d", fontsize=8.2)
            if c == 3:
                v = rows[r - 1][3]
                if v.startswith("✗"):
                    cell.set_facecolor("#fdecec")
                    cell.set_text_props(color="#b91c1c", fontweight="bold", fontsize=8.2)
                elif v.startswith("✓"):
                    cell.set_text_props(color="#15803d", fontsize=8.2)
                elif v.startswith("?"):
                    cell.set_text_props(color="#b45309", fontsize=8.2)
                else:
                    cell.set_text_props(color="#9ca3af", fontsize=8.2)
            if c == 0:
                cell.set_text_props(color=rows[r - 1][4], fontweight="bold", fontsize=8.6)
        cell.PAD = 0.032

    if commits:
        fig.text(0.012, 0.070, "最近提交", fontsize=8.6, fontweight="bold", color="#444")
        for i, line in enumerate(commits):
            fig.text(0.012, 0.046 - i * 0.024, "· " + line[:92], fontsize=7.4, color="#666")

    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def main():
    os.makedirs(OUT, exist_ok=True)
    sh(["git", "pull", "-q", "--rebase"], cwd=REPO)
    marks, gk = run_gatekeeper()
    data = collect()
    commits = recent_commits()
    png = os.path.join(OUT, "dashboard.png")
    try:
        render(data, commits, png, marks, gk)
    except Exception as e:
        print("[warn] render failed: %s" % e, file=sys.stderr)
        return

    total = sum(len(v) for v in data.values())
    done = sum(1 for v in data.values() for _, d in v if d)
    print("**openlegs 儀表板** — %s" % datetime.now(HKT).strftime("%m-%d %H:%M"))
    print("")
    for label, short, _c, _k in TRACKS:
        items = data.get(label, [])
        print("• %s：%d 項追蹤，%d 完成" % (label, len(items), sum(1 for _, d in items if d)))
    print("• 合計 %d 項，%d 完成" % (total, done))
    if gk:
        print("• 法案核實：%d 條已查，%d 條待處理" % (gk["checked"], gk["blocked"]))
        if gk["blocked"]:
            print("  ⚠️ 有未核實/標題不符條目，已在表內標紅")
    print("")
    print("MEDIA:%s" % png)


if __name__ == "__main__":
    main()
