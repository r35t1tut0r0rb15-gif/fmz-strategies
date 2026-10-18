# #436123 Stochastic Vortex Strategy -> `fmz_436123_stochastic_vortex_entry_hold`

- FMZ source id: 436123 (lineage).
- Source: https://www.fmz.com/strategy/436123 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-21 15:12:37). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C86). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic cross and the Vortex index |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_period` [14, 21] x `length_vi` [14, 21]: **4 trials**; %D 3 and slowing 3 fixed.

## Ambiguities resolved

- No exit: the long is held. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
