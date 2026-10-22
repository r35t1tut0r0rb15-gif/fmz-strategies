# #489032 Multi Indicator Dynamic Crossover Trend Following Quantitative Strategy Analysis -> `fmz_489032_sma5_20_cross_rsi_bb_filter_atr2_4_bracket_reversal`

- FMZ source id: 489032 (lineage).
- Source: https://www.fmz.com/strategy/489032 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-01 13:30:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C268). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | SMA crossings with RSI / Bollinger filters and an ATR bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [2.0, 1.0] x `tp_atr` [4.0, 2.0]: **4 trials**; SMA 5 / 20, RSI 14, BB 20 / 2, ATR 14.

## Ambiguities resolved

- The bracket is armed from the fill bar (the source: the bar after). Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
