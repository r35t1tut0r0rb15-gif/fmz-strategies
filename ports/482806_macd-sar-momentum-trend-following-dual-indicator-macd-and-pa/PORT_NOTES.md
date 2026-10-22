# #482806 动量趋势跟踪型双指标MACD与抛物线SAR结合策略-Momentum-Trend-Following-Dual-Indicator-MACD-and-Parabolic-SAR-Combination-Strategy -> `fmz_482806_macd12_26_9_side_sar_side_state_reversal`

- FMZ source id: 482806 (lineage).
- Source: https://www.fmz.com/strategy/482806 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:45:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C250). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD side with the SAR side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_len` [12, 8] x `sar_max` [0.2, 0.1]: **4 trials**; MACD slow 26 / signal 9, SAR start 0.02 / step 0.02.

## Ambiguities resolved

- Repeat state entries add nothing; the opposite state reverses. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
