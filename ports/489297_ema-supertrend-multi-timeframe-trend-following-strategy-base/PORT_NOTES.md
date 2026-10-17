# #489297 基于EMA和Supertrend结合的多时间框架趋势跟踪策略-Multi-timeframe-Trend-Following-Strategy-Based-on-EMA-and-Supertrend-Combination -> `fmz_489297_supertrend_flip_ema_filter`

- FMZ source id: 489297 (lineage).
- Source: https://www.fmz.com/strategy/489297 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-03 11:23:13). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR bands and EMAs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`multiplier` [3.0, 2.0] x `slow` [15, 30]: **4 trials**; defaults 3 / 15 (the source's); EMA 9 and ATR 10 fixed.

## Ambiguities resolved

- The SuperTrend as written (Wilder ATR; bands seeded by nz). The short close on every up-trend bar acts on the
  position held at the bar's start; a long exits only by the reversing short.
- REVERSAL INTENDED. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
