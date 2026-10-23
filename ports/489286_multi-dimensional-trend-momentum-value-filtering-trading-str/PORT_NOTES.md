# #489286 Multi Dimensional Trend Momentum Value Filtering Trading Strategy -> `fmz_489286_adx_rsi_stochrsi_extreme_vs_daily_hlc3_reversal`

- FMZ source id: 489286 (lineage).
- Source: https://www.fmz.com/strategy/489286 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-03 15:16:18). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI / stochastic RSI extremes in a strong ADX, against the bar's typical price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_min` [25.0, 20.0] x `rsi_lo` [30.0, 25.0]: **4 trials** (RSI high = 100 - low); stoch RSI 20 / 80, ADX 14.

## Ambiguities resolved

- Daily VWAP = the bar's hlc3; no exit. Volume a common factor only. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "oscillator_reversion"`.

## Marks

`none`
