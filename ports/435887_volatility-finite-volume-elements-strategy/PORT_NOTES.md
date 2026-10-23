# #435887 Volatility Finite Volume Elements Strategy -> `fmz_435887_money_flow_move_volatility_cutoff_state_reversal`

- FMZ source id: 435887 (lineage).
- Source: https://www.fmz.com/strategy/435887 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-19 15:23:59). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Money-flow move against a volatility cutoff |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`samples` [22, 50] x `cintra` [0.1, 0.2]: **4 trials**; Cinter 0.1.

## Ambiguities resolved

- Volume only plotted. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_state"`.

## Marks

`none`
