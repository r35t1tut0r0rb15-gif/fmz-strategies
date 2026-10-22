# #453264 基于连续K线动态网格自适应均线动态止损策略-Continuous-Candle-Based-Dynamic-Grid-Adaptive-Moving-Average-with-Dynamic-Stop-Loss-Strategy -> `fmz_453264_three_rising_closes_low_test_stop_long`

- FMZ source id: 453264 (lineage).
- Source: https://www.fmz.com/strategy/453264 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 16:16:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C191). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stop is a close test on the low |
| 2 | PASS | Three-close runs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_pct` [0.11, 0.05]: **2 trials**; the 3-close runs fixed.

## Ambiguities resolved

- The stop is a low test at the bar close. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
