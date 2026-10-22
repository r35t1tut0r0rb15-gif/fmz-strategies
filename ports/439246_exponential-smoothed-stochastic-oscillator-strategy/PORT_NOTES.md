# #439246 Exponential Smoothed Stochastic Oscillator Strategy -> `fmz_439246_power_stochastic_20_80_cross`

- FMZ source id: 439246 (lineage).
- Source: https://www.fmz.com/strategy/439246 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-18 15:53:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C119). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21] x `ex` [2, 5]: **4 trials**; levels 20 / 80 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
