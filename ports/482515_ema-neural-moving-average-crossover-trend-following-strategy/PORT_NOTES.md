# #482515 神经均线交叉趋势跟踪策略结合EMA过滤系统-Neural-Moving-Average-Crossover-Trend-Following-Strategy-with-EMA-Filtering-System -> `fmz_482515_ema200_side_sma9_15_cross_reentry`

- FMZ source id: 482515 (lineage).
- Source: https://www.fmz.com/strategy/482515 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 18:29:13). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | SMAs and an EMA. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow` [15, 30] x `trend` [200, 100]: **4 trials**; defaults 15 / 200 (the source's); SMA 9 fixed.

## Ambiguities resolved

- The `barssince(cross) > 0` re-entries hold the EMA 200 side on every bar after the first cross of that side.
- A closing cross is followed by a same-side re-entry on that bar, which meets the still-open position (pyramiding
  1) and is ignored: one flat bar, re-entry on the next (as written).
- Closes act on the position held at the bar's start and never undo an entry on that bar (#430850); an exit and an
  opposite entry on one bar become the entry alone. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
