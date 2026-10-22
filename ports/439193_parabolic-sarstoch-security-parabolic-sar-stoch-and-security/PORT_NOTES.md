# #439193 基于Parabolic-SARStoch和Security指标的多时间框架量化交易策略Parabolic-SAR-Stoch-and-Security-Indicator-Based-Multi-Timeframe-Quantitative-Trading-Strategy -> `fmz_439193_psar_stoch_last_3h_bar`

- FMZ source id: 439193 (lineage).
- Source: https://www.fmz.com/strategy/439193 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-18 11:40:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C117). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SAR side, stochastic levels and the last 3-hour bar's colour |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period_k` [14, 9] x `sar_max` [0.2, 0.1]: **4 trials**; SAR start / increment 0.01 and the 3-hour size fixed.

## Ambiguities resolved

- Lower-timeframe values = the day's last 3-hour bar; SAR side as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
