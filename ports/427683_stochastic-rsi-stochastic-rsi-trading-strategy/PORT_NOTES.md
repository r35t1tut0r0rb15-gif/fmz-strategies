# #427683 Stochastic RSI Trading Strategy -> `fmz_427683_hpotter_stoch_rsi_bands`

- FMZ source id: 427683 (lineage).
- Source: https://www.fmz.com/strategy/427683 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-23 15:59:22). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`top` [80, 70] x `low` [20, 30] x `length_rsi` [14, 7]: **8 trials**; defaults 80 / 20 / 14 (the source's); stoch 14 and K 3 fixed.

## Ambiguities resolved

- "Trade reverse" fixed off; D drawn only. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
