# #484921 Multi Indicator Trend Confirmation Dynamic Risk Management Trading Strategy -> `fmz_484921_close_supertrend3_10_cross_ema200_rsi50_atr_bracket_reversal`

- FMZ source id: 484921 (lineage).
- Source: https://www.fmz.com/strategy/484921 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-05 10:19:52). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C262). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | SuperTrend line crossings with EMA / RSI filters |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `atr_multiplier` [1.5, 2.0]: **4 trials**; ATR 10, EMA 200, RSI 14, target 2R.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`coarse_bar_stop`
