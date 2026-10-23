# #491042 Multi Indicator Dynamic Position Size Volatility Adaptive Quantitative Trading Strategy -> `fmz_491042_ema9_21_rsi_macd_stoch_ichimoku_cloud_reversal`

- FMZ source id: 491042 (lineage).
- Source: https://www.fmz.com/strategy/491042 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-18 09:55:17). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V48). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA trend with momentum pullback filters and the Ichimoku cloud |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (position size plotted only). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_fast` [9, 12] x `ema_slow` [21, 26]: **4 trials**; RSI 14 at 50, MACD 12 / 26 / 9, stoch 14 / 3, Ichimoku 9 / 26 / 52.

## Ambiguities resolved

- Same-timeframe security = the chart; spans undisplaced. Volume not used. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_agreement"`.

## Marks

`none`
