# #474953 动态波动率指标VIDYA结合ATR趋势跟踪反转策略-Dynamic-Volatility-Index-VIDYA-with-ATR-Trend-Following-Reversal-Strategy -> `fmz_474953_vidya10_atr200_band_break_reversal`

- FMZ source id: 474953 (lineage).
- Source: https://www.fmz.com/strategy/474953 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-13 10:21:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C226). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Adaptive-average ATR band breaks |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vidya_length` [10, 20] x `band` [2.0, 1.5]: **4 trials**; momentum 20.

## Ambiguities resolved

- VIDYA seeded at 0, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
