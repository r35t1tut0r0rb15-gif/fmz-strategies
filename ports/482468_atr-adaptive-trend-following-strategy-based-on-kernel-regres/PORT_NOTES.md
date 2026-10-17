# #482468 基于核回归和ATR动态波段的自适应趋势跟踪策略-Adaptive-Trend-Following-Strategy-Based-on-Kernel-Regression-and-ATR-Dynamic-Bands -> `fmz_482468_rq_kernel_atr_envelope_fade_always_in`

- FMZ source id: 482468 (lineage).
- Source: https://www.fmz.com/strategy/482468 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 15:33:21). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A kernel average and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`coef` [2.7, 2.0] x `h` [8, 16]: **4 trials**; defaults 2.7 / 8 (the source's); r 8, x_0 25 and ATR 32 fixed.

## Ambiguities resolved

- The source array holds one value, so the kernel loop runs over lags 0 to 26 (size + x_0); past values only. The
  lagged estimate and the colour logic feed no order.
- The closes repeat the reversal. REVERSAL INTENDED (always in). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

none
