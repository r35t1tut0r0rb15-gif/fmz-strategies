# #491508 Multi Indicator Momentum Strategy with EMA Crossover and Risk Management -> `fmz_491508_ema9_21_cross_rsi_macd_sl1_tp2pct_reversal`

- FMZ source id: 491508 (lineage).
- Source: https://www.fmz.com/strategy/491508 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-21 16:00:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C274). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | EMA crossings with RSI / MACD confirmation and a percent bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slPercent` [1.0, 2.0] x `tpPercent` [2.0, 4.0]: **4 trials**; EMA 9 / 21, RSI 14, MACD 12 / 26 / 9.

## Ambiguities resolved

- Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
