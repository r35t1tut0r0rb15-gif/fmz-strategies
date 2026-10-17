# #434712 Price Volatility Breakout Strategy Based on Double Moving Averages -> `fmz_434712_dpmo_colour_states`

- FMZ source id: 434712 (lineage).
- Source: https://www.fmz.com/strategy/434712 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-08 16:44:22). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C71). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A momentum oscillator's colour states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [35, 20] x `siglen` [10, 5]: **4 trials**; the second smoothing 20 fixed.

## Ambiguities resolved

- Smoothing seeded at 0; same-bar entry beats the close. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
