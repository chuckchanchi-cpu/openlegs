# Push handoff for @Openclaw

**Date:** 2026-11-15 09:35 HKT
**From:** fring1122-agent
**Task:** Chuck asked you to help upload this work to the GitHub repo.

## Blocker

This machine has **no stored GitHub credentials**. `git push` fails:

```
fatal: could not read Username for 'https://github.com': terminal prompts disabled
fatal: Cannot prompt because user interactivity has been disabled.
```

Git Credential Manager (`credential.helper=manager`) needs an interactive window, which a non-interactive exec call cannot provide.

## What is ready to push

Repo: `C:\Users\chuck\.openclaw\workspace\openlegs`
Branch: `main`, **1 commit ahead of origin/main**

```
eaf3fe4 Add policy-exposure matrix + daily tracker
  dashboard.html               |  40 +-
  data/donor-daily-prev.json   | 1050 +++++++++++++++++
  data/donor-daily.json        | 1050 +++++++++++++++++
  data/donor-matrix.json       |  165 ++++
  donor-matrix.html            |  154 ++++
  scripts/donor_tracker.js     |  217 ++++
  6 files changed, 2660 insertions(+), 16 deletions(-)
```

`donor-matrix.png` is intentionally untracked (build artifact, already in `.gitignore`).

## The one command

```bash
cd C:\Users\chuck\.openclaw\workspace\openlegs
git push origin main
```

Your gateway has GitHub credentials already (you pushed `c33799d` earlier), so this should work from your side. If it does not, the alternative is to copy the 6 files into your own clone and commit there — but the commit is already made, so a plain push is cleaner.

## What this commit contains — please review before pushing

**1. New: policy-exposure matrix** (`data/donor-matrix.json`)
34 tickers, each scored −3…+3 on seven policy-transmission dimensions:
`subsidy`, `govContract`, `regulation`, `rates`, `wealthTax`, `crypto`, `tariff`.
Plus three falsifiable hypotheses with explicit pass/falsify thresholds and a 2027-02-03 deadline.

**2. New: daily tracker** (`scripts/donor_tracker.js`)
Fetches Yahoo Finance daily closes, aggregates baskets by group and by donor lean, computes hypothesis verdicts. Runs daily at 18:30 HKT (automation `b7bac857`).

**3. New: matrix page** (`donor-matrix.html`)
Standalone page rendering the full matrix and hypotheses. Not yet linked from the nav, only from the dashboard section.

**4. Corrected: `dashboard.html`** — three numbers on your mirror-indicator table were wrong:

| Ticker | Was shown | Actual (Yahoo, verified) |
|---|---|---|
| FSLR | +9.4% | **−7.8%** |
| TSLA | −3.6% | **−2.1%** |
| GEO | −3.8% | **+15.9%** |

Also: the "民主黨金主（選後全線升）" heading was withdrawn — the D basket was **−0.82%** after the election, i.e. a negative return, not a rally. GEO is the sharpest reversal of all (R-donor, rose 15.9% after the R loss).

**5. Why the framework changed**
Same-party baskets diverge by up to 20pp:
- D side: BigTech **+4.64%** vs CleanEnergy **−4.58%**
- R side: PrivatePrison **+8.43%** vs Crypto **−13.85%**

Donor identity therefore has weak explanatory power. The matrix replaces it with policy exposure. The party baskets are retained as a comparison, not as the thesis.

## Results worth noting for the dashboard

Basket averages (election 2026-11-03 → 2026-11-13, 7 trading days):

```
             runup_1w   since_election   1y        ytd
D basket      +1.04%       -0.82%       +2.56%   -2.74%   (n=17)
R basket      -1.70%       -4.48%      +19.36%  +13.32%   (n=16)
S&P 500       -1.99%        0.00%      +13.32%  +10.42%
```

Hypothesis verdicts (7-day sample — treat as provisional):
- **H1** D−R = +3.66pp → in the passing band (≥ +2.0pp) but sample far too short
- **H2** Crypto−SPY = −13.85pp → in the passing band (≤ −3.0pp)
- **H3** |corr(exposure, return)| = **0.366** vs |corr(donor lean, return)| = **0.235** → exposure explains more, **but the sign is negative**: higher exposure scores fell more. This contradicts the naive reading and is worth flagging rather than hiding.

## Caveats to keep visible on the dashboard

1. 7 trading days is not evidence. MSOS alone can move ±10% in a day and it distorts any equal-weighted average it sits in.
2. The exposure scores are **analyst judgement, not measurement**. They are hypotheses.
3. H3's negative sign means "policy exposure matters" is currently supported, but "Democratic-friendly exposure → outperformance" is **not**.

## Please do not

- Do not re-add `$527B` for the CHIPS Act (correct: $280B authorised / $52.7B appropriated).
- Do not restore the "+9.4% FSLR" figures.
- Do not present the mirror indicator as causal — it is a correlation screen.
