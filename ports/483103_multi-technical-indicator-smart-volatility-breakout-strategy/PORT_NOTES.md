# #483103 Multi Technical Indicator Smart Volatility Breakout Strategy -> `fmz_483103_bb20_lower_stoch_cross_atr_spike_atr1_5_bracket_long`

- FMZ source id: 483103 (lineage).
- Source: https://www.fmz.com/strategy/483103 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 13:42:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C257). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | Band / Stochastic reversals in high volatility |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 1.2] x `bb_length` [20, 40]: **4 trials**; Stochastic 14 / 3 / 3, ATR 14 (the multiplier sets both the threshold and the bracket).

## Ambiguities resolved

- A repeat signal's re-sent bracket is pending. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
