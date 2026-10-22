# #444341 G-Channel与EMA结合的趋势跟踪策略G-Channel-and-EMA-Trend-Following-Strategy -> `fmz_444341_gchannel_bull_ema9_pullback_long`

- FMZ source id: 444341 (lineage).
- Source: https://www.fmz.com/strategy/444341 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-11 11:08:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C170). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | G-Channel state with an EMA pullback |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 50] x `ema_length` [9, 21]: **4 trials**.

## Ambiguities resolved

- nz() seeds as written; bearish until both crossings seen. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
