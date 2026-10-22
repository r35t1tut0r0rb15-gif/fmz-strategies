# #473234 高级时间框架Fibonacci回撤与高低点条件突破交易系统-Advanced-Timeframe-Fibonacci-Retracement-with-High-Low-Breakout-Trading-System -> `fmz_473234_prev_bar_half_range_level_extremes_reversal`

- FMZ source id: 473234 (lineage).
- Source: https://www.fmz.com/strategy/473234 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 15:01:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C214). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Previous-bar level and extreme filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`low_look` [20, 50] x `high_look` [10, 20] x `level` [0.5, 0.618]: **8 trials**.

## Ambiguities resolved

- The "Last" daily candle is the previous bar (as written). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
