# #436767 Momentum Direction Divergence Strategy -> `fmz_436767_ergodic_csi_zone_state`

- FMZ source id: 436767 (lineage).
- Source: https://www.fmz.com/strategy/436767 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-27 15:37:31). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C95). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Dimensionless index zones |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`r` [32, 20] x `smth_len` [5, 10]: **4 trials**; length 1, big point value 1 and the zones 0.004 / 0.024 fixed; reverse off.

## Ambiguities resolved

- State entries sent on every bar of the state; fixnan carried by hand. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
