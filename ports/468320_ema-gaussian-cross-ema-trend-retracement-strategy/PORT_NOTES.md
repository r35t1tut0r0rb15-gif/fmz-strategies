# #468320 高斯交叉EMA趋势滑点追踪策略-Gaussian-Cross-EMA-Trend-Retracement-Strategy -> `fmz_468320_strong_green_candle_half_retrace_ema44_slope_long`

- FMZ source id: 468320 (lineage).
- Source: https://www.fmz.com/strategy/468320 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 15:34:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C207). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Strong-candle pullbacks with a sloped EMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [44, 21] x `flat_frac` [0.0000119, 0.001]: **4 trials**; the 50 % retrace fixed.

## Ambiguities resolved

- Slope threshold as a fraction of 42000. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
