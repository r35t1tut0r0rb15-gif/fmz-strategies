# #439649 Dynamic Momentum Oscillator Trading Strategy -> `fmz_439649_hpotter_dynamo_oscillator_state`

- FMZ source id: 439649 (lineage).
- Source: https://www.fmz.com/strategy/439649 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-22 17:28:39). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C122). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A normalised stochastic |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`osc_len` [10, 14] x `ma_len` [20, 30]: **4 trials**; bands 77 / 23 fixed.

## Ambiguities resolved

- Running extremes from the data start, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
