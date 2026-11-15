#!/usr/bin/env python3
"""gatekeeper.py — verify every bill citation before it reaches the dashboard.

Scans radar/*.md and reports/*.md for bill references (H.R. 10846, S. 1234,
H.Res. 57...), extracts the claimed title from the surrounding text, and
verifies each with verify_bill.py.

Output: a JSON verdict map used by openlegs_dashboard.py to mark each row
VERIFIED / MISMATCH / UNVERIFIED, plus a list of blockers.

A MISMATCH means the bill number is real but the claimed title is wrong.
Those entries must not be published.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

REPO = os.path.expanduser("~/.openclaw/workspace/openlegs-repo")
sys.path.insert(0, os.path.join(REPO, "scripts"))

try:
    import verify_bill
except Exception as e:            # pragma: no cover
    print("[gatekeeper] cannot import verify_bill: %s" % e, file=sys.stderr)
    verify_bill = None

BILL_RE = re.compile(
    r"\b(H\.?\s?R\.?|H\.?\s?Res\.?|S\.?\s?Res\.?|S\.?)\s*(\d{1,5})\b", re.I)

# "H.R. 10846 (IH) Pay Your Taxes Avoided by Borrowing Act of 2026"
TITLE_INLINE = re.compile(
    r"(?:H\.?\s?R\.?|S\.?|H\.?\s?Res\.?|S\.?\s?Res\.?)\s*\d{1,5}\s*"
    r"(?:\([A-Z]{1,4}\))?\s*[—\-–:.]?\s*(.{6,120})", re.U)


def norm_type(tok):
    t = re.sub(r"[\s.]", "", tok).lower()
    if t in ("hr",):
        return "hr"
    if t in ("hres",):
        return "hres"
    if t in ("s",):
        return "s"
    if t in ("sres",):
        return "sres"
    return "hr"


def gather():
    """Return [(source_file, bill_type, number, claimed_title), ...]"""
    found = []
    for sub in ("radar", "reports"):
        d = os.path.join(REPO, sub)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md"):
                continue
            path = os.path.join(d, fn)
            try:
                body = open(path, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            for line in body.splitlines():
                if not BILL_RE.search(line):
                    continue
                # skip lines that are obviously historical example lists
                if "實為" in line or "actual " in line.lower():
                    continue
                for m in BILL_RE.finditer(line):
                    btype = norm_type(m.group(1))
                    num = m.group(2)
                    rest = line[m.end():]
                    rest = re.sub(r"^\s*(?:\([A-Z]{1,4}\))?", "", rest)
                    rest = re.sub(r"^[\s—\-–:.,、]+", "", rest)
                    # stop at a URL, table pipe, or double space
                    claim = re.split(r"https?://|\||  ", rest)[0].strip()
                    claim = claim.strip("*_` ")
                    if len(claim) < 5:
                        claim = ""
                    found.append((fn, btype, num, claim[:120]))
    # de-dupe by (type, number), keep the longest claim
    best = {}
    for fn, bt, num, claim in found:
        k = (bt, num)
        if k not in best or len(claim) > len(best[k][3]):
            best[k] = (fn, bt, num, claim)
    return list(best.values())


def main():
    if verify_bill is None:
        print("[]")
        return
    rows = gather()
    out = []
    blockers = []
    for fn, bt, num, claim in rows:
        try:
            res = verify_bill.check("119", bt, num, claim)
        except Exception as e:
            res = {"type": bt.upper(), "number": num, "claimed_title": claim,
                   "match": "ERROR", "safe_to_publish": False,
                   "warning": "lookup failed: %s" % e}
        res["source_file"] = fn
        out.append(res)
        if not res.get("safe_to_publish"):
            blockers.append(res)

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "checked": len(out),
        "blocked": len(blockers),
        "results": out,
    }
    dest = os.path.expanduser("~/.openclaw/workspace/state/openlegs/gatekeeper.json")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    for r in out:
        print("%-8s %-6s %-9s %s" % (
            r.get("type", "?"), r.get("number", "?"), r.get("match", "?"),
            (r.get("claimed_title") or "")[:56]))
    print("\n%d checked, %d blocked" % (len(out), len(blockers)))


if __name__ == "__main__":
    main()
