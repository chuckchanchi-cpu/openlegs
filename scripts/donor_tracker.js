#!/usr/bin/env node
/**
 * donor_tracker.js — daily policy-exposure vs donor-party tracker
 *
 * Reads data/donor-matrix.json (policy exposure scores + hypotheses),
 * fetches fresh prices from Yahoo Finance, writes data/donor-daily.json.
 *
 * Outputs:
 *   - per-ticker returns across 4 windows
 *   - basket returns by group / by donorLean / by exposure quintile
 *   - H1 / H2 / H3 current values vs falsification thresholds
 *
 * Usage: node scripts/donor_tracker.js [--quiet]
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const MATRIX = path.join(ROOT, 'data', 'donor-matrix.json');
const OUT = path.join(ROOT, 'data', 'donor-daily.json');
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)';

const ELECTION = '2026-11-03';
const PRE_ELECTION = '2026-10-27';
const YTD = '2026-01-01';

function daysAgo(n) {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString().slice(0, 10);
}

async function fetchSeries(symbol) {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}?range=2y&interval=1d`;
  const res = await fetch(url, { headers: { 'User-Agent': UA } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const j = await res.json();
  const r = j.chart?.result?.[0];
  if (!r) throw new Error('no result');
  const ts = r.timestamp || [];
  const cl = r.indicators?.quote?.[0]?.close || [];
  const rows = [];
  for (let i = 0; i < ts.length; i++) {
    if (cl[i] == null) continue;
    rows.push({ date: new Date(ts[i] * 1000).toISOString().slice(0, 10), close: cl[i] });
  }
  return rows;
}

function pctBetween(series, fromDate, toDate) {
  const a = series.find((x) => x.date >= fromDate);
  const tail = series.filter((x) => x.date <= toDate);
  const b = tail[tail.length - 1];
  if (!a || !b || !a.close) return null;
  return Math.round(((b.close - a.close) / a.close) * 10000) / 100;
}

function mean(arr) {
  const v = arr.filter((x) => x != null);
  if (!v.length) return null;
  return Math.round((v.reduce((s, x) => s + x, 0) / v.length) * 100) / 100;
}

// composite exposure score: sum of the 7 policy dimensions
function exposureScore(t) {
  const dims = ['subsidy', 'govContract', 'regulation', 'rates', 'wealthTax', 'crypto', 'tariff'];
  const vals = dims.map((d) => Number(t[d] || 0));
  return vals.reduce((s, x) => s + x, 0);
}

function pearson(xs, ys) {
  const n = xs.length;
  if (n < 3) return null;
  const mx = xs.reduce((s, x) => s + x, 0) / n;
  const my = ys.reduce((s, y) => s + y, 0) / n;
  let num = 0, dx = 0, dy = 0;
  for (let i = 0; i < n; i++) {
    const a = xs[i] - mx, b = ys[i] - my;
    num += a * b; dx += a * a; dy += b * b;
  }
  if (!dx || !dy) return null;
  return Math.round((num / Math.sqrt(dx * dy)) * 1000) / 1000;
}

async function main() {
  const quiet = process.argv.includes('--quiet');
  const matrix = JSON.parse(fs.readFileSync(MATRIX, 'utf8'));
  const today = new Date().toISOString().slice(0, 10);

  const results = [];
  for (const t of matrix.tickers) {
    process.stdout.write(quiet ? '' : `${t.t} `);
    try {
      const s = await fetchSeries(t.t);
      const last = s[s.length - 1];
      results.push({
        ticker: t.t,
        name: t.name,
        group: t.group,
        donorLean: t.donorLean,
        exposure: exposureScore(t),
        dims: {
          subsidy: t.subsidy, govContract: t.govContract, regulation: t.regulation,
          rates: t.rates, wealthTax: t.wealthTax, crypto: t.crypto, tariff: t.tariff,
        },
        lastDate: last.date,
        lastClose: Math.round(last.close * 100) / 100,
        ret: {
          runup_1w: pctBetween(s, PRE_ELECTION, ELECTION),
          since_election: pctBetween(s, ELECTION, today),
          ytd: pctBetween(s, YTD, today),
          y1: pctBetween(s, daysAgo(365), today),
          d7: pctBetween(s, daysAgo(7), today),
          d30: pctBetween(s, daysAgo(30), today),
        },
      });
    } catch (e) {
      if (!quiet) console.log(`FAIL ${e.message}`);
    }
    await new Promise((r) => setTimeout(r, 300));
  }
  if (!quiet) console.log('');

  // basket aggregation
  function basketBy(pred, field) {
    const v = results.filter(pred).map((r) => r.ret[field]).filter((x) => x != null);
    return mean(v);
  }
  const groups = [...new Set(results.map((r) => r.group))];
  const baskets = {
    byDonor: {
      D: { since_election: basketBy((r) => r.donorLean === 'D', 'since_election'), runup_1w: basketBy((r) => r.donorLean === 'D', 'runup_1w'), y1: basketBy((r) => r.donorLean === 'D', 'y1'), ytd: basketBy((r) => r.donorLean === 'D', 'ytd'), n: results.filter((r) => r.donorLean === 'D').length },
      R: { since_election: basketBy((r) => r.donorLean === 'R', 'since_election'), runup_1w: basketBy((r) => r.donorLean === 'R', 'runup_1w'), y1: basketBy((r) => r.donorLean === 'R', 'y1'), ytd: basketBy((r) => r.donorLean === 'R', 'ytd'), n: results.filter((r) => r.donorLean === 'R').length },
    },
    byGroup: {},
  };
  for (const g of groups) {
    baskets.byGroup[g] = {
      since_election: basketBy((r) => r.group === g, 'since_election'),
      runup_1w: basketBy((r) => r.group === g, 'runup_1w'),
      y1: basketBy((r) => r.group === g, 'y1'),
      ytd: basketBy((r) => r.group === g, 'ytd'),
      exposure: exposureScore(matrix.tickers.find((t) => t.group === g) || {}),
      n: results.filter((r) => r.group === g).length,
    };
  }

  // hypotheses
  const spy = results.find((r) => r.ticker === 'SPY');
  const spyRet = spy ? spy.ret.since_election : 0;
  const cryptoRet = basketBy((r) => r.group === 'Crypto', 'since_election');
  const dRet = baskets.byDonor.D.since_election;
  const rRet = baskets.byDonor.R.since_election;

  const valid = results.filter((r) => r.ret.since_election != null);
  const corrExposure = pearson(valid.map((r) => r.exposure), valid.map((r) => r.ret.since_election));
  const corrDonor = pearson(
    valid.filter((r) => r.donorLean === 'D' || r.donorLean === 'R').map((r) => (r.donorLean === 'D' ? 1 : 0)),
    valid.filter((r) => r.donorLean === 'D' || r.donorLean === 'R').map((r) => r.ret.since_election)
  );

  const hypotheses = {
    H1: {
      metric: 'D basket minus R basket, since election',
      value: dRet != null && rRet != null ? Math.round((dRet - rRet) * 100) / 100 : null,
      pass: '>= +2.0 pp',
      falsify: '< 0.0 pp',
      verdict: dRet != null && rRet != null ? ((dRet - rRet) < 0 ? 'FALSIFIED' : ((dRet - rRet) >= 2 ? 'PASSING' : 'INCONCLUSIVE')) : 'NO DATA',
    },
    H2: {
      metric: 'crypto basket minus SPY, since election',
      value: cryptoRet != null && spyRet != null ? Math.round((cryptoRet - spyRet) * 100) / 100 : null,
      pass: '<= -3.0 pp',
      falsify: '> -1.0 pp',
      verdict: cryptoRet != null && spyRet != null ? ((cryptoRet - spyRet) > -1 ? 'FALSIFIED' : ((cryptoRet - spyRet) <= -3 ? 'PASSING' : 'INCONCLUSIVE')) : 'NO DATA',
    },
    H3: {
      metric: '|corr(policy exposure, return)| vs |corr(donor lean, return)|',
      exposureCorr: corrExposure,
      donorCorr: corrDonor,
      pass: 'exposure |r| > donor |r|',
      verdict: corrExposure != null && corrDonor != null
        ? (Math.abs(corrExposure) > Math.abs(corrDonor) ? 'PASSING' : 'FALSIFIED')
        : 'NO DATA',
    },
  };

  const payload = {
    generatedAt: new Date().toISOString(),
    asOfTradingDate: results.length ? results[0].lastDate : null,
    windows: { election: ELECTION, preElection: PRE_ELECTION, ytd: YTD },
    baskets,
    hypotheses,
    tickers: results,
  };

  fs.writeFileSync(OUT, JSON.stringify(payload, null, 2), 'utf8');

  if (!quiet) {
    console.log('=== BASKETS (since election / runup 1w / 1y / ytd) ===');
    for (const [k, v] of Object.entries(baskets.byDonor)) {
      console.log(`  ${k} (n=${v.n}): ${v.since_election}% / ${v.runup_1w}% / ${v.y1}% / ${v.ytd}%`);
    }
    console.log('=== GROUPS ===');
    for (const [g, v] of Object.entries(baskets.byGroup)) {
      console.log(`  ${g.padEnd(14)} expo=${String(v.exposure).padStart(3)} n=${v.n} elec=${String(v.since_election).padStart(7)}% runup=${String(v.runup_1w).padStart(7)}%`);
    }
    console.log('=== HYPOTHESES ===');
    for (const [id, h] of Object.entries(hypotheses)) {
      console.log(`  ${id}: ${h.verdict}  (${h.metric})`);
    }
    console.log(`\nSAVED ${OUT}`);
  }
}

main().catch((e) => { console.error(e); process.exit(1); });
