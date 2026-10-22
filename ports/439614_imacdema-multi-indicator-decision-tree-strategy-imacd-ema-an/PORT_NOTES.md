# #439614 多指标决策树策略IMACDEMA和一目均衡表Multi-Indicator-Decision-Tree-Strategy-IMACD-EMA-and-Ichimoku -> `fmz_439614_impulse_macd_colour_cloud_ema40`

- FMZ source id: 439614 (lineage).
- Source: https://www.fmz.com/strategy/439614 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-22 11:25:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C122). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed averages and Ichimoku lines |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [40, 20] x `length_ma` [34, 21]: **4 trials**; Ichimoku 9 / 26 / 52 / 26 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
