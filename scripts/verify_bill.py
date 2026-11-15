#!/usr/bin/env python3
"""verify_bill.py — check that a bill number's TITLE matches a claimed title.

Why this exists
---------------
An LLM can emit a bill number that really exists but pair it with an invented
title. That is the most dangerous hallucination for legislative research:
the number passes a naive "does it exist?" check, so the whole entry looks
verified. Verified example (2026-11-15):
  claimed  H.R.158 = "Chip Security Act"      actual CLEAN Elections Act
  claimed  H.R.159 = "Chip Security Act"      actual CLEAN Public Service Act
  claimed  H.R.313 = chip-related             actual Natural Gas Tax Repeal Act
  claimed  H.R.1188 = "No American Chips..."  actual Police CAMERA Act of 2025
The real Chip Security Act is H.R.3447.

Data sources
------------
1. Congress.gov API (optional, richer) - key read from
   ~/.openclaw/secrets/congress-api-key or $CONGRESS_API_KEY.
   Gives official title, sponsor, status, and the full /titles alias list.
2. govinfo.gov bill text HTML (no key needed) - predictable path:
   https://www.govinfo.gov/content/pkg/BILLS-<congress><type><number><ver>/html/....htm
   Gives the SHORT title the bill calls itself.

Why both: the API `title` field is often a condensed formal title, NOT the
short title. Verified 2026-11-16 on H.R.10846:
   API title     = "Pay Your TAB Act of 2026"
   govinfo short = "Pay Your Taxes Avoided by Borrowing Act"
Comparing against the API title alone would false-MISMATCH a correct citation.
So a match against ANY title from ANY source counts.

Usage
-----
  python3 verify_bill.py 119 hr 3447 --claim "Chip Security Act"
  python3 verify_bill.py --batch claims.json

Exit codes
  0  EXACT or CLOSE
  1  MISMATCH  (number real, title wrong -> do not publish)
  2  NOT_FOUND (no version text found -> unverified, treat as unsafe)
"""
import argparse
import difflib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

# version suffixes worth trying, most common first
VERSIONS = ["ih", "is", "eh", "es", "rh", "rs", "enr", "pcs", "rfs", "rfh", "rds"]

UA = "openlegs-verify/1.0 (legislative fact-check)"
TIMEOUT = 20


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            if r.status != 200:
                return None
            return r.read().decode("utf-8", "ignore")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None


def _clean_title(raw):
    """Pull the SHORT title out of a govinfo bill HTML document.

    govinfo uses LaTeX-style quotes: ``Chip Security Act''
    The short title lives in SECTION 1, which is what we must match against -
    the long title ("To require the Secretary of Commerce...") is a different
    string and would produce false MISMATCH verdicts.
    """
    text = re.sub(r"<[^>]+>", " ", raw)
    text = re.sub(r"\s+", " ", text)

    # canonical: SECTION 1. SHORT TITLE. This Act may be cited as the ``X''.
    m = re.search(
        r"(?:may be cited as|may be cited as the)\s*[:\s]*"
        r"(?:``|\"|\u201c|')?\s*(.{4,180}?)\s*(?:''|\"|\u201d|')?\s*\.",
        text, re.I)
    if m:
        return _tidy(m.group(1))

    # fallback: the short title heading followed on the same line
    m = re.search(r"SHORT TITLE\.?\s*(.{4,180}?)\.", text, re.I)
    if m:
        return _tidy(m.group(1))

    return None


def _tidy(title):
    """Strip govinfo's LaTeX-style quoting: the ``Chip Security Act''"""
    t = title.strip(" .;")
    # order matters: "the ``X''" -> drop the article first, then the quotes
    for _ in range(3):
        t = re.sub(r"^the\s+", "", t, flags=re.I)
        t = re.sub(r'^[`\u201c\u201d"\']+\s*', "", t)
        t = re.sub(r'\s*[`\u201c\u201d"\']+$', "", t)
    return t.strip(" .;") or None


def short_titles(raw):
    """Return ALL short-title alternatives for a bill.

    Many bills carry two: "may be cited as the ``Long Formal Name'' or the
    ``Short Name''". Matching only the first produces false MISMATCH when the
    caller cites the short one.
    """
    text = re.sub(r"<[^>]+>", " ", raw)
    text = re.sub(r"\s+", " ", text)
    m = re.search(
        r"(?:may be cited as|may be cited as the)\s*[:\s]*"
        r"(?:``|\"|\u201c|')?\s*(.{4,260}?)\s*(?:''|\"|\u201d|')?\s*\.",
        text, re.I)
    blob = m.group(1) if m else None
    if not blob:
        m2 = re.search(r"SHORT TITLE\.?\s*(.{4,260}?)\.", text, re.I)
        blob = m2.group(1) if m2 else None
    if not blob:
        return []
    # split on the dual-title connector, keeping quote marks out of the split
    parts = re.split(r"\s*or the\s*|\s*''\s*or\s*``\s*", blob, flags=re.I)
    out = []
    for p in parts:
        t = _tidy(p)
        if t and len(t) >= 4:
            out.append(t)
    return out


def lookup(congress, btype, number):
    """Try each version suffix until one returns text. Returns (titles, version_url)."""
    for v in VERSIONS:
        pkg = "BILLS-%s%s%s%s" % (congress, btype.lower(), number, v)
        url = "https://www.govinfo.gov/content/pkg/%s/html/%s.htm" % (pkg, pkg)
        body = _get(url)
        if not body:
            continue
        titles = short_titles(body)
        if titles:
            return titles, url
    return [], None


def api_key():
    """Congress.gov key from env, else the 600-mode secrets file."""
    k = os.environ.get("CONGRESS_API_KEY", "").strip()
    if k:
        return k
    path = os.path.expanduser("~/.openclaw/secrets/congress-api-key")
    try:
        with open(path) as f:
            return f.read().strip()
    except OSError:
        return ""


def api_lookup(congress, btype, number):
    """Congress.gov API: title + /titles aliases + metadata. None if no key."""
    key = api_key()
    if not key:
        return None
    base = "https://api.congress.gov/v3/bill/%s/%s/%s" % (congress, btype.lower(), number)
    q = "?format=json&api_key=" + urllib.parse.quote(key)
    raw = _get(base + q)
    if not raw:
        return None
    try:
        b = json.loads(raw).get("bill", {})
    except Exception:
        return None
    titles = []
    if b.get("title"):
        titles.append(b["title"])
    traw = _get(base + "/titles" + q)
    if traw:
        try:
            for t in json.loads(traw).get("titles", []):
                if t.get("title"):
                    titles.append(t["title"])
        except Exception:
            pass
    seen, uniq = set(), []
    for t in titles:
        k = re.sub(r"\s+", " ", t.lower()).strip()
        if k not in seen:
            seen.add(k)
            uniq.append(re.sub(r"\s+", " ", t).strip())
    return {
        "titles": uniq,
        "introduced": b.get("introducedDate"),
        "sponsor": (b.get("sponsors") or [{}])[0].get("fullName", ""),
        "latestAction": (b.get("latestAction") or {}).get("text", ""),
        "url": base,
    }


def compare(claimed, actual):
    if not actual:
        return "NOT_FOUND", 0.0
    a = re.sub(r"[^a-z0-9 ]", "", claimed.lower()).strip()
    b = re.sub(r"[^a-z0-9 ]", "", actual.lower()).strip()
    if a == b:
        return "EXACT", 1.0
    ratio = difflib.SequenceMatcher(None, a, b).ratio()
    if a in b or b in a:
        return "CLOSE", max(ratio, 0.8)
    if ratio >= 0.72:
        return "CLOSE", ratio
    return "MISMATCH", ratio


def check(congress, btype, number, claimed):
    """Verify across BOTH sources; a match against any title from any source wins."""
    api = api_lookup(congress, btype, number)
    gv_titles, gv_url = lookup(congress, btype, number)

    all_titles, sources = [], []
    if api:
        all_titles.extend(api["titles"])
        sources.append("congress.gov/api")
    if gv_titles:
        all_titles.extend(gv_titles)
        sources.append("govinfo.gov/text")

    # de-dupe case-insensitively
    seen, uniq = set(), []
    for t in all_titles:
        k = re.sub(r"\s+", " ", t.lower()).strip()
        if k and k not in seen:
            seen.add(k)
            uniq.append(t)

    best_verdict, best_score, best_title = "NOT_FOUND", 0.0, None
    rank = {"NOT_FOUND": 0, "MISMATCH": 1, "CLOSE": 2, "EXACT": 3}
    for t in uniq:
        v, s = compare(claimed or "", t)
        if rank[v] > rank[best_verdict] or (rank[v] == rank[best_verdict] and s > best_score):
            best_verdict, best_score, best_title = v, s, t

    out = {
        "congress": congress,
        "type": btype.upper(),
        "number": number,
        "claimed_title": claimed,
        "actual_title": best_title or (uniq[0] if uniq else None),
        "alternatives": uniq[:8],
        "match": best_verdict,
        "score": round(best_score, 3),
        "sources_used": sources,
        "source": gv_url or (api["url"] if api else None),
        "safe_to_publish": best_verdict in ("EXACT", "CLOSE"),
    }
    if api:
        out["meta"] = {"introduced": api["introduced"], "sponsor": api["sponsor"],
                       "latestAction": api["latestAction"]}

    if best_verdict == "MISMATCH":
        out["warning"] = ("DANGEROUS: bill number is real but the claimed title is wrong. "
                          "Do not publish this entry.")
    elif best_verdict == "NOT_FOUND":
        out["warning"] = ("No bill text or API record found. Either the bill does not exist, "
                          "or it is not published yet. Treat as UNVERIFIED.")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("congress", nargs="?", default="119")
    ap.add_argument("btype", nargs="?", default="hr")
    ap.add_argument("number", nargs="?")
    ap.add_argument("--claim", default="")
    ap.add_argument("--batch", help="JSON file: [{congress,type,number,claimed}]")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.batch:
        rows = json.load(open(args.batch))
        results = [check(r.get("congress", "119"), r.get("type", "hr"),
                         r["number"], r.get("claimed", "")) for r in rows]
        bad = [r for r in results if not r["safe_to_publish"]]
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=1))
        else:
            for r in results:
                print("%-6s %-5s %-6s %-12s %s" % (
                    r["type"], r["number"], r["match"],
                    (r["actual_title"] or "?")[:48], "" if r["safe_to_publish"] else "!!"))
        print("\n%d/%d safe to publish" % (len(results) - len(bad), len(results)))
        sys.exit(0 if not bad else 1)

    if not args.number:
        ap.error("number is required unless --batch is used")

    res = check(args.congress, args.btype, args.number, args.claim)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print("bill      : %s %s %s" % (res["type"], res["number"], res["congress"]))
        print("claimed   : %s" % (res["claimed_title"] or "(none)"))
        print("actual    : %s" % (res["actual_title"] or "(not found)"))
        print("verdict   : %s (score %.2f)" % (res["match"], res["score"]))
        if res.get("warning"):
            print("warning   : %s" % res["warning"])
        if res["source"]:
            print("source    : %s" % res["source"])

    sys.exit(0 if res["safe_to_publish"] else (1 if res["match"] == "MISMATCH" else 2))


if __name__ == "__main__":
    main()
