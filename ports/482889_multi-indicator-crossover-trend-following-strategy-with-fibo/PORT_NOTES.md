# #482889 多指标交叉趋势跟踪策略结合斐波那契回调及止盈止损优化系统-Multi-Indicator-Crossover-Trend-Following-Strategy-with-Fibonacci-Retracement-and-Stop-Loss-Take-Profit-Optimization-System -> `fmz_482889_ema9_21_cross_pct_bracket_2_4`

- FMZ source id: 482889 (lineage).
- Source: https://www.fmz.com/strategy/482889 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 16:43:42). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar. |
| 2 | PASS | Moving averages and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [2.0, 1.0] x `tp_pct` [4.0, 6.0]: **4 trials**; defaults 2 / 4 (the source's); EMA 9 / 21 fixed.

## Ambiguities resolved

- The Fibonacci levels and the trend label only feed plots. Crosses alternate: no re-placement.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
