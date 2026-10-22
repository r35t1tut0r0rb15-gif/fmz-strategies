# #474037 自适应权重趋势跟踪策略VIDYA多指标组合系统-Adaptive-Weighted-Trend-Following-Strategy-VIDYA-Multi-Indicator-System -> `fmz_474037_vidya21_cmo9_direction_reversal`

- FMZ source id: 474037 (lineage).
- Source: https://www.fmz.com/strategy/474037 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-05 15:07:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C220). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Adaptive average direction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pds` [21, 50]: **2 trials**; CMO length 9, CMO method.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
