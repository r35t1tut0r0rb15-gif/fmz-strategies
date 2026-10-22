# #473346 Adaptive-FVG-Detection-and-MA-Trend-Trading-Strategy-with-Dynamic-Resistance-基于时适-FVG-检测与移动平均趋势的动态阻力交易策略 -> `fmz_473346_fvg_reversal_candle_sma20_high50_target_long`

- FMZ source id: 473346 (lineage).
- Source: https://www.fmz.com/strategy/473346 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 14:50:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C216). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Gap-retest reversal candles with an SMA filter and a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent stop stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_pct` [0.02, 0.04] x `lookback` [50, 100] x `ma_period` [20, 50]: **8 trials**.

## Ambiguities resolved

- The short closes at its own fill (wrong-side limit): sent as the long's exit (as #452827). Repeat-signal re-sends not followed. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
