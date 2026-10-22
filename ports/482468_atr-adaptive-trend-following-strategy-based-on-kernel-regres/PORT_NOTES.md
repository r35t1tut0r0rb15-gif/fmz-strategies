# #482468 基于核回归和ATR动态波段的自适应趋势跟踪策略-Adaptive-Trend-Following-Strategy-Based-on-Kernel-Regression-and-ATR-Dynamic-Bands -> `fmz_482468_rq_kernel27_atr32_band_cross_fade_reversal`

- FMZ source id: 482468 (lineage).
- Source: https://www.fmz.com/strategy/482468 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 15:33:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C245). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Kernel-estimate band crossings (counter-trend entries) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`coef` [2.7, 2.0] x `h` [8.0, 16.0]: **4 trials**; r 8, 27 bars, ATR 32.

## Ambiguities resolved

- The kernel window is fixed at 27 bars (size 1 + x_0 25 + 1), as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion_band"`.

## Marks

`none`
