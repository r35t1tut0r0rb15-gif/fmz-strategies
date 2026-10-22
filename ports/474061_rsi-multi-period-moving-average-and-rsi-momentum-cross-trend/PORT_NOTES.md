# #474061 多周期均线与RSI动量交叉趋势跟踪策略-Multi-Period-Moving-Average-and-RSI-Momentum-Cross-Trend-Following-Strategy -> `fmz_474061_sma9_21_cross_rsi_extreme_or_engulfing_reversal`

- FMZ source id: 474061 (lineage).
- Source: https://www.fmz.com/strategy/474061 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-05 16:43:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C221). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings at RSI extremes or engulfing candles |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**; the RSI levels fixed.

## Ambiguities resolved

- The short wins a bar with both signals (call order). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
