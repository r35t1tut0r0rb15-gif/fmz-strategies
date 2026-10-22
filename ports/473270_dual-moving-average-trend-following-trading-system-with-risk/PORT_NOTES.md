# #473270 Dual Moving Average Trend Following Trading System with Risk Reward Ratio Optimization Strategy -> `fmz_473270_first_close_over_ema20_ema200_trend_long_bracket_pending`

- FMZ source id: 473270 (lineage).
- Source: https://www.fmz.com/strategy/473270 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 17:20:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C216). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | First EMA 20 closes in an EMA 20 / 200 uptrend; bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (the EMA lengths are constants; the bracket is pending).

## Ambiguities resolved

- Bracket armed only by repeat signals: pending, no exit (as #437800). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop_pending`
