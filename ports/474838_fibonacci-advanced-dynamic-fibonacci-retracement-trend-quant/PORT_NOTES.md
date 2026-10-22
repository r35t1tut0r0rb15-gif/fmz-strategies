# #474838 高级动态Fibonacci回撤趋势量化交易策略-Advanced-Dynamic-Fibonacci-Retracement-Trend-Quantitative-Trading-Strategy -> `fmz_474838_fib618_100bar_range_cross_long_exit_pending`

- FMZ source id: 474838 (lineage).
- Source: https://www.fmz.com/strategy/474838 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 14:32:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C224). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Fibonacci-level crossings; moving range exit described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [100, 50] x `level` [0.618, 0.5]: **4 trials**; the exit pending.

## Ambiguities resolved

- Moving range exit pending, no exit (trailing_stop_pending). Long only.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`trailing_stop_pending`
