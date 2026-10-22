# #474881 自适应趋势跟踪与反转识别策略基于ZigZag与Aroon指标的量化交易系统-Adaptive-Trend-Following-and-Reversal-Detection-Strategy-A-Quantitative-Trading-System-Based-on-ZigZag-and-Aroon-Indicators -> `fmz_474881_aroon14_cross_zigzag5_filter_reversal`

- FMZ source id: 474881 (lineage).
- Source: https://www.fmz.com/strategy/474881 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 17:21:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C226). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Aroon crossings with a zig-zag filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`depth` [5, 10] x `aroon_length` [14, 25]: **4 trials**.

## Ambiguities resolved

- Aroon ties counted as the most recent bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
