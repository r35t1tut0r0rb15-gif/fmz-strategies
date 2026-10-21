# #438792 极化分形效率PFE交易策略Polarized-Fractal-Efficiency-PFE-Trading-Strategy -> `fmz_438792_polarized_fractal_efficiency_state`

- FMZ source id: 438792 (lineage).
- Source: https://www.fmz.com/strategy/438792 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-15 14:01:25). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C112). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit constants -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`unit` [2.4e-05, 0.0] x `length` [9, 18]: **4 trials**; EMA 5 and the 50 / -50 bands fixed.

## Ambiguities resolved

- Price-unit constants -> fractions of the close. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
