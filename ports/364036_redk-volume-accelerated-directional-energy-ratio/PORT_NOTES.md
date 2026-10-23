# #364036 RedK Volume Accelerated Directional Energy Ratio -> `fmz_364036_redk_vader9_relative_volume_energy_zero_cross_reversal`

- FMZ source id: 364036 (lineage).
- Source: https://www.fmz.com/strategy/364036 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-18 15:30:50). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
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

`length` [9, 14] x `vlookbk` [10, 20]: **4 trials**; average 5, smooth 3, WMA.

## Ambiguities resolved

- Volume = broker tick volume (relative to its own recent range). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
