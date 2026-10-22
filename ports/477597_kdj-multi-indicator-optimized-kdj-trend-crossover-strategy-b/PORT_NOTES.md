# #477597 多指标优化型KDJ趋势交叉策略基于动态随机形态的交易系统-Multi-Indicator-Optimized-KDJ-Trend-Crossover-Strategy-Based-on-Dynamic-Stochastic-Pattern-Trading-System -> `fmz_477597_kdj90_3_30_jd_cross_pct_stop_long`

- FMZ source id: 477597 (lineage).
- Source: https://www.fmz.com/strategy/477597 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-06 16:23:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C235). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; avg-price stop as a fraction of the fill |
| 2 | PASS | KDJ J / D crossings with a percent stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 1 stored, not ported; the stop percentage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [90, 30] x `d_signal` [30, 10]: **4 trials**; K signal 3, stop 5 %.

## Ambiguities resolved

- bcwsma recursion as written. Long only. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`coarse_bar_stop`
