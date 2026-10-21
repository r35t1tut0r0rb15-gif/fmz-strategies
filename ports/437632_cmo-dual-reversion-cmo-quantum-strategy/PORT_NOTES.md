# #437632 双重反转CMO量子策略Dual-Reversion-CMO-Quantum-Strategy -> `fmz_437632_reversal123_cmo_wma_combo`

- FMZ source id: 437632 (lineage).
- Source: https://www.fmz.com/strategy/437632 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-04 14:35:23). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C103). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and a dimensionless momentum |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND429948. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_cmo` [14, 28]: **4 trials**; K smoothing 1, D 3, level 50 and WMA 13 fixed; reverse off.

## Ambiguities resolved

- 123 test as written; state entries; state 0 closes. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
