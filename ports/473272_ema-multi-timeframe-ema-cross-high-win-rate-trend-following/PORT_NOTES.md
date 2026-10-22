# #473272 多周期EMA交叉高胜率趋势跟踪策略进阶版-Multi-Timeframe-EMA-Cross-High-Win-Rate-Trend-Following-Strategy-Advanced -> `fmz_473272_close_cross_ema20_stacked_trend_long_bracket_pending`

- FMZ source id: 473272 (lineage).
- Source: https://www.fmz.com/strategy/473272 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 17:27:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C216). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA 20 cross-ups in a stacked uptrend; bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (the EMA lengths are constants; the bracket is pending).

## Ambiguities resolved

- Bracket armed only by repeat signals: pending, no exit (as #437800). Long only.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop_pending`
