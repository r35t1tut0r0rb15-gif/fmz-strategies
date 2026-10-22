# #439350 基于斐波那契平均K线和移动平均线的量化交易策略Fibonacci-Average-Candle-with-Moving-Average-Strategy-for-Quantitative-Trading -> `fmz_439350_fibonacci_average_candle_long`

- FMZ source id: 439350 (lineage).
- Source: https://www.fmz.com/strategy/439350 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-19 14:36:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C120). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Lagged price averages and EMAs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow_ema` [55, 89]: **2 trials**; the lag set and the other EMAs fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
