# #489186 高级多功能SuperTrend趋势跟踪策略与自动止盈止损系统-Advanced-Multi-functional-SuperTrend-Trend-Following-Strategy-with-Automated-Take-Profit-and-Stop-Loss-System -> `fmz_489186_handbuilt_supertrend10_3_flip_reversal_3d`

- FMZ source id: 489186 (lineage).
- Source: https://www.fmz.com/strategy/489186 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-02 15:30:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C270). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend flips |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [3.0, 2.0] x `atrPeriod` [10, 20]: **4 trials**.

## Ambiguities resolved

- Labels-only TP / SL are not orders. REVERSAL INTENDED. FREQ = "3D" (three broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
