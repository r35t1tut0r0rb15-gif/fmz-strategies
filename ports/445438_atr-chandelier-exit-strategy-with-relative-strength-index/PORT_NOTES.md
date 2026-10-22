# #445438 ATR Chandelier Exit Strategy with Relative Strength Index -> `fmz_445438_chandelier_cross_rsi_extreme_atr_bracket_reversal`

- FMZ source id: 445438 (lineage).
- Source: https://www.fmz.com/strategy/445438 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-19 14:05:52). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C172). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed on the signal bar (re-sent levels marked) |
| 2 | PASS | Chandelier-line crossings at RSI extremes with an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [3.0, 2.0] x `sl_atr` [2.0, 1.0]: **4 trials**; the ATR and RSI lengths, the RSI levels and the 1-ATR target fixed.

## Ambiguities resolved

- Levels from the signal bar; repeat-signal moves not followed (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`trailing_stop_pending`
