# #437651 Momentum Trend Tracking Strategy -> `fmz_437651_kwan_nrp_direction`

- FMZ source id: 437651 (lineage).
- Source: https://www.fmz.com/strategy/437651 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-04 15:28:06). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C103). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Dimensionless oscillator product |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_momentum` [9, 14] x `length_rsi` [9, 14]: **4 trials**; stochastic 9 and NRP 2 fixed; reverse off.

## Ambiguities resolved

- Array average of the last two pushed values; stochastic length hard-coded 9; state 0 closes. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
