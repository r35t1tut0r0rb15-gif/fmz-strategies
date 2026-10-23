# #365322 RedK Dual VADER with Energy Bars -> `fmz_365322_redk_vader10_relative_volume20_energy_zero_cross_reversal`

- FMZ source id: 365322 (lineage).
- Source: https://www.fmz.com/strategy/365322 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-24 11:49:07). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume-weighted directional energy zero crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `vlookbk` [20, 10]: **4 trials**; average 5, smooth 3, WMA.

## Ambiguities resolved

- Same core as #364036 (rule 7). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
