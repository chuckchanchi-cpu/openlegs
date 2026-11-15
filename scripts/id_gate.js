#!/usr/bin/env node
/**
 * id_gate.js — enforce verifiable identifiers in radar/report files
 *
 * Rule (Chuck, 2026-11-16): every tracked item must carry a bill number,
 * Federal Register citation, or docket id. A policy trend with no identifier
 * is a to-do, not a fact.
 *
 * This scans radar/ and reports/ for tracking items that describe legislation
 * or regulatory action but carry no identifier, and prints them so they can be
 * fixed. It also extracts every existing identifier for the verifier to check.
 *
 * Usage:
 *   node scripts/id_gate.js            # report gaps
 *   node scripts/id_gate.js --json     # machine output
 *   node scripts/id_gate.js --extract  # only print extracted identifiers
 *
 * Exit: 0 = all items sourced, 1 = gaps found
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const DIRS = ['radar', 'reports'];

// identifier patterns
const PATTERNS = [
  { kind: 'bill',    re: /\b(H\.?\s?R\.?|S\.?)\s?(\d{1,5})\b/g },
  { kind: 'fr',      re: /\b(\d{2})\s?FR\s?(\d{4,6})\b/g },
  { kind: 'docket',  re: /\bdocket\s+(?:no\.?\s*)?([A-Z0-9-]{4,})/gi },
  { kind: 'pl',      re: /\bP\.?L\.?\s?(\d{2,3})-(\d{1,4})\b/g },
  { kind: 'crs',     re: /\bR(\d{4,5})\b/g },
];

// phrases that indicate a trackable legislative/regulatory claim needing an id.
// Narrow on purpose: definitional prose ("EAR is the Export Administration
// Regulations") is not a claim to verify and must not be flagged, or the gate
// becomes noise and gets ignored.
const CLAIM_HINTS = [
  '法案', '草案', '修正案', '條例',
  'bill', 'act of', 'amendment', 'markup', 'introduced',
];

// these make a line a tracking item rather than an explanatory sentence
const TRACK_MARKERS = ['[ ]', '[x]', '追蹤', 'track', '待跟', '下一輪'];

// lines explicitly marked pending are allowed to lack ids
const ALLOW_MARKERS = ['待補編號', '待證', '待核', '未確認', '傳聞', 'TODO', '待辦', '需 BIS', '需查', '待查'];

function extractIds(text) {
  const found = [];
  for (const { kind, re } of PATTERNS) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(text)) !== null) {
      found.push({ kind, raw: m[0].trim() });
    }
  }
  // dedupe
  const seen = new Set();
  return found.filter((x) => {
    const k = `${x.kind}|${x.raw}`;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

function scanFile(file) {
  const text = fs.readFileSync(file, 'utf8');
  const lines = text.split(/\r?\n/);
  const gaps = [];

  // consider list items and table rows as trackable entries
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();
    if (!trimmed) continue;

    const isListItem = /^([-*+]|\d+\.)\s+/.test(trimmed);
    const isTableRow = trimmed.startsWith('|') && !/^\|[\s:|-]+\|$/.test(trimmed);
    if (!isListItem && !isTableRow) continue;

    // A trackable claim needs BOTH a legislative noun AND evidence that this
    // line is a tracking entry, not a definition. Definitions of statutes and
    // regulations are reference material, not assertions awaiting a source.
    const lower = trimmed.toLowerCase();
    const hasClaimNoun = CLAIM_HINTS.some((h) => lower.includes(h.toLowerCase()));
    if (!hasClaimNoun) continue;

    const isTrackItem = TRACK_MARKERS.some((m) => lower.includes(m.toLowerCase()))
      || /^\s*-\s*\[\s?\]/.test(line);
    if (!isTrackItem) continue;

    const hasId = extractIds(trimmed).length > 0;
    const allowed = ALLOW_MARKERS.some((m) => trimmed.includes(m));
    if (!hasId && !allowed) {
      gaps.push({ file: path.relative(ROOT, file), line: i + 1, text: trimmed.slice(0, 160) });
    }
  }
  return { ids: extractIds(text), gaps };
}

function main() {
  const args = process.argv.slice(2);
  const jsonMode = args.includes('--json');
  const extractOnly = args.includes('--extract');

  const files = [];
  for (const d of DIRS) {
    const dir = path.join(ROOT, d);
    if (!fs.existsSync(dir)) continue;
    for (const f of fs.readdirSync(dir)) {
      if (f.endsWith('.md')) files.push(path.join(dir, f));
    }
  }

  const allIds = [];
  const allGaps = [];
  for (const f of files) {
    const { ids, gaps } = scanFile(f);
    allIds.push(...ids.map((x) => ({ ...x, file: path.relative(ROOT, f) })));
    allGaps.push(...gaps);
  }

  if (extractOnly) {
    console.log(JSON.stringify(allIds, null, 2));
    return 0;
  }

  if (jsonMode) {
    console.log(JSON.stringify({ scannedFiles: files.length, identifiers: allIds, gaps: allGaps }, null, 2));
    return allGaps.length ? 1 : 0;
  }

  console.log(`=== identifier gate ===`);
  console.log(`scanned ${files.length} files in ${DIRS.join('/')}`);
  console.log(`identifiers found: ${allIds.length}`);
  for (const id of allIds) {
    console.log(`  [${id.kind}] ${id.raw}  (${id.file})`);
  }

  if (!allGaps.length) {
    console.log('\nNo gaps. Every legislative claim carries an identifier or a pending marker.');
    return 0;
  }

  console.log(`\ngaps: ${allGaps.length} item(s) describe legislation with no identifier and no pending marker`);
  for (const g of allGaps) {
    console.log(`  ${g.file}:${g.line}`);
    console.log(`    ${g.text}`);
  }
  console.log('\nFix by adding a bill number, FR citation, or one of: 待補編號 / 待證 / 待核');
  return 1;
}

process.exit(main());
