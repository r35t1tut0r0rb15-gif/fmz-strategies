# #440806 Stochastic Moving Average Strategy with Double Filters -> `fmz_440806_stoch_oversold_turn_ema_exit_long`

- FMZ source id: 440806 (lineage).
- Source: https://www.fmz.com/strategy/440806 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-02 11:28:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C140). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested stop |
| 2 | PASS | Stochastic, EMA and a close stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 14] x `lossp` [13, 5]: **4 trials**; the other settings fixed.

## Ambiguities resolved

- Close-tested percent stop. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
