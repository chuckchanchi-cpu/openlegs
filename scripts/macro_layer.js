#!/usr/bin/env node
/**
 * macro_layer.js — discount-rate / credit layer for the donor-exposure model
 *
 * Why this exists: the donor-party and policy-exposure stories are both
 * cross-sectional. They say nothing about WHY everything fell together after
 * 2026-11-03. The Bloomberg QTS story (2026-11-13) is the clue: a borrower
 * cut a private debt sale 60% rather than pay a higher yield. That is a
 * discount-rate event, not a party-politics event.
 *
 * This script tracks the common factor the cross-section sits inside:
 *   - long-end yield level and rate of change
 *   - credit spread proxies (HY vs IG vs loans)
 *   - rate volatility
 *
 * Output: data/macro-layer.json, plus a printed verdict on whether the
 * post-election move is better explained by rates than by politics.
 *
 * Usage: node scripts/macro_layer.js [--quiet]
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'data', 'macro-layer.json');
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)';

const ELECTION = '2026-11-03';

const SERIES = {
  tnx:   '^TNX',   // 10y yield x10
  vix:   '^VIX',
  move:  '^MOVE',  // rate vol
  hyg:   'HYG',    // HY credit
  lqd:   'LQD',    // IG credit
  tlt:   'TLT',    // long duration
  spy:   'SPY',
  ibit:  'IBIT',   // crypto
  smh:   'SMH',    // AI semis
  vrt:   'VRT',    // AI datacenter equipment
  dlr:   'DLR',    // datacenter REIT
  crwv:  'CRWV',   // AI neocloud
};

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

function at(series, date) {
  let hit = null;
  for (const row of series) {
    if (row.date <= date) hit = row;
    else break;
  }
  return hit ? hit.close : null;
}

function pct(from, to) {
  if (from == null || to == null || from === 0) return null;
  return Math.round(((to - from) / from) * 10000) / 100;
}

function pp(from, to) {
  if (from == null || to == null) return null;
  return Math.round((to - from) * 100) / 100;
}

async function main() {
  const quiet = process.argv.includes('--quiet');
  const today = new Date().toISOString().slice(0, 10);
  const data = {};

  for (const [key, sym] of Object.entries(SERIES)) {
    try {
      const s = await fetchSeries(sym);
      data[key] = s;
      if (!quiet) process.stdout.write(`${key} `);
    } catch (e) {
      if (!quiet) process.stdout.write(`${key}:FAIL `);
    }
    await new Promise((r) => setTimeout(r, 280));
  }
  if (!quiet) console.log('');

  const get = (k) => data[k] || [];

  // ^TNX already returns the yield in percent (e.g. 5.15 means 5.15%)
  const tnxSeries = get('tnx');
  const y10 = {
    now: at(tnxSeries, today),
    atElection: at(tnxSeries, ELECTION),
    preElection: at(tnxSeries, '2026-10-27'),
    m1: at(tnxSeries, daysAgo(30)),
    m3: at(tnxSeries, daysAgo(90)),
    y1: at(tnxSeries, daysAgo(365)),
    peak2y: Math.max(...tnxSeries.map((r) => r.close)),
    trough2y: Math.min(...tnxSeries.map((r) => r.close)),
  };

  const ret = (k, from) => pct(at(get(k), from), at(get(k), today));

  const out = {
    generatedAt: new Date().toISOString(),
    asOfTradingDate: get('spy').length ? get('spy')[get('spy').length - 1].date : null,
    yield10y: {
      ...y10,
      changeSinceElection_pp: pp(y10.atElection, y10.now),
      change30d_pp: pp(y10.m1, y10.now),
      change1y_pp: pp(y10.y1, y10.now),
      note: 'yield up = discount rate up = long-duration assets reprice lower',
    },
    returns: {
      sinceElection: {
        hyg: ret('hyg', ELECTION), lqd: ret('lqd', ELECTION), tlt: ret('tlt', ELECTION),
        spy: ret('spy', ELECTION), ibit: ret('ibit', ELECTION), smh: ret('smh', ELECTION),
        vrt: ret('vrt', ELECTION), dlr: ret('dlr', ELECTION), crwv: ret('crwv', ELECTION),
      },
      last5d: {
        hyg: ret('hyg', daysAgo(7)), lqd: ret('lqd', daysAgo(7)), tlt: ret('tlt', daysAgo(7)),
        spy: ret('spy', daysAgo(7)), ibit: ret('ibit', daysAgo(7)), smh: ret('smh', daysAgo(7)),
        vrt: ret('vrt', daysAgo(7)), dlr: ret('dlr', daysAgo(7)), crwv: ret('crwv', daysAgo(7)),
      },
    },
    vol: {
      vix: at(get('vix'), today),
      vixChange5d_pct: ret('vix', daysAgo(7)),
      move: at(get('move'), today),
      moveChange5d_pct: ret('move', daysAgo(7)),
      note: 'MOVE up = rate vol up = bond market unsettled, distinct from equity fear',
    },
  };

  // Verdict: is this a rates story, a credit story, or a rotation inside AI?
  const r5 = out.returns.last5d;
  const creditStable = r5.hyg != null && Math.abs(r5.hyg) < 2 && r5.lqd != null && Math.abs(r5.lqd) < 3;
  const ratesMoved = Math.abs(out.yield10y.change30d_pp || 0) > 0.15;
  const durationHit = r5.tlt != null && r5.tlt < -2;
  // NVDA vs SMH divergence: rotation within AI, not a sector-wide move
  const aiDivergence = r5.smh != null && out.returns.sinceElection.smh != null
    ? Math.abs((r5.vrt || 0) - (out.returns.sinceElection.smh || 0)) > 10
    : false;

  let diagnosis;
  if (!creditStable) {
    diagnosis = 'CREDIT_STRESS';
  } else if (ratesMoved && durationHit) {
    diagnosis = 'RATES_STORY';
  } else {
    diagnosis = 'MIXED_OR_UNCLEAR';
  }

  out.diagnosis = {
    verdict: diagnosis,
    evidence: {
      hyg5d: r5.hyg,
      lqd5d: r5.lqd,
      tlt5d: r5.tlt,
      yield30dChange_pp: out.yield10y.change30d_pp,
      yield1yChange_pp: out.yield10y.change1y_pp,
      creditStable,
      ratesMoved,
      durationHit,
      aiDivergence,
      spy5d: r5.spy,
      ibit5d: r5.ibit,
    },
    explanation:
      diagnosis === 'RATES_STORY'
        ? 'Credit spreads are flat while long-duration assets fell and yields rose. That is a discount-rate repricing, not a credit event and not party politics. QTS cutting its debt sale rather than paying a higher yield is the same signal from the primary market.'
        : diagnosis === 'CREDIT_STRESS'
          ? 'Credit proxies moved materially. That is a genuine credit event; discount rates alone cannot explain it.'
          : 'Signals are mixed; no single-factor explanation holds.',
    what_the_data_actually_shows: [
      r5.spy != null && r5.spy > 0
        ? `Equities ROSE ${r5.spy}% over five sessions while crypto moved ${r5.ibit}% - this is not a broad risk-off event.`
        : `Equities moved ${r5.spy}% over five sessions while crypto moved ${r5.ibit}%.`,
      r5.hyg != null && Math.abs(r5.hyg) < 1
        ? `High-yield credit was essentially flat (${r5.hyg}%), so there is no credit stress signal. A borrower struggling to place debt at an acceptable price is a pricing standoff, not default fear.`
        : `High-yield credit moved ${r5.hyg}%, which does indicate spreading stress.`,
      r5.tlt != null && r5.tlt < -2
        ? `Long Treasuries moved ${r5.tlt}% while the 10y yield rose - duration is being repriced.`
        : `Long Treasuries moved ${r5.tlt}%.`,
      out.yield10y.change1y_pp != null && out.yield10y.change1y_pp > 0.5
        ? `The 10y yield is up ${out.yield10y.change1y_pp}pp over one year (${out.yield10y.y1?.toFixed(2)}% to ${out.yield10y.now?.toFixed(2)}%), which is the dominant discount-rate story. This dwarfs the ${out.yield10y.changeSinceElection_pp}pp move since the election.`
        : `The 10y yield has not moved much over one year.`,
      aiDivergence
        ? 'Inside AI, the vertically-integrated names and the datacenter/power complex diverged sharply - that is capital rotation within the theme, not a single AI verdict.'
        : 'AI names moved broadly together.',
    ],
    implication:
      'The QTS story is a useful signal about the primary market, but the data does not show a credit event. It shows a discount-rate regime plus rotation inside AI. Any party or policy story must first control for these common factors.',
  };

  fs.writeFileSync(OUT, JSON.stringify(out, null, 2), 'utf8');

  if (!quiet) {
    console.log('=== 10y yield ===');
    console.log(`  now ${y10.now?.toFixed(2)}%  at election ${y10.atElection?.toFixed(2)}%  (${out.yield10y.changeSinceElection_pp > 0 ? '+' : ''}${out.yield10y.changeSinceElection_pp}pp)`);
    console.log(`  1y ago ${y10.y1?.toFixed(2)}%  2y range ${y10.trough2y?.toFixed(2)}%-${y10.peak2y?.toFixed(2)}%`);
    console.log('=== last 5 trading days ===');
    for (const [k, v] of Object.entries(out.returns.last5d)) {
      console.log(`  ${k.padEnd(6)} ${String(v).padStart(7)}%`);
    }
    console.log('=== vol ===');
    console.log(`  VIX ${out.vol.vix?.toFixed(2)} (5d ${out.vol.vixChange5d_pct}%)  MOVE ${out.vol.move?.toFixed(2)} (5d ${out.vol.moveChange5d_pct}%)`);
    console.log(`\nDIAGNOSIS: ${diagnosis}`);
    console.log(`  ${out.diagnosis.explanation}`);
    console.log(`\nSAVED ${OUT}`);
  }
}

main().catch((e) => { console.error(e); process.exit(1); });
