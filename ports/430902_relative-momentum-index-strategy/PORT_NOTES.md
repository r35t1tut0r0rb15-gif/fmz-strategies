# #430902 Relative Momentum Index Strategy -> `fmz_430902_relative_momentum_index`

- FMZ source id: 430902 (lineage).
- Source: https://www.fmz.com/strategy/430902 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-02 17:21:45). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A momentum oscillator's levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10] x `buy_zone` [40, 30]: **4 trials**; SellZone 70 fixed.

## Ambiguities resolved

- Recursions and seeds as written. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
