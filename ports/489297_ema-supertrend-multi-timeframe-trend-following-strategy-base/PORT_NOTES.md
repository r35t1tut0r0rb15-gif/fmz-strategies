# #489297 基于EMA和Supertrend结合的多时间框架趋势跟踪策略-Multi-timeframe-Trend-Following-Strategy-Based-on-EMA-and-Supertrend-Combination -> `fmz_489297_supertrend10_3_flip_ema9_15_side_reversal`

- FMZ source id: 489297 (lineage).
- Source: https://www.fmz.com/strategy/489297 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-03 11:23:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C271). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend flips with an EMA side filter |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`Multiplier` [3.0, 2.0] x `Periods` [10, 20]: **4 trials**; EMA 9 / 15.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
