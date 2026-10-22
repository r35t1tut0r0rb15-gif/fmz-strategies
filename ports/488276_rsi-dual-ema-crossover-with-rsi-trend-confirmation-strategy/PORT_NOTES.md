# #488276 双指数移动平均线交叉与RSI趋势确认策略-Dual-EMA-Crossover-with-RSI-Trend-Confirmation-Strategy -> `fmz_488276_ema9_21_cross_rsi30_filter_exits_reversal`

- FMZ source id: 488276 (lineage).
- Source: https://www.fmz.com/strategy/488276 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 14:44:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C266). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with an RSI filter and exits |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**; RSI 14 / 30.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
