# #437769 Reversal Momentum Compound Strategy -> `fmz_437769_reversal123_dapd_combo`

- FMZ source id: 437769 (lineage).
- Source: https://www.fmz.com/strategy/437769 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-05 14:06:21). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C105). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and an average-range band |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_dapd` [21, 42]: **4 trials**; K smoothing 1, D 3 and level 50 fixed; reverse off.

## Ambiguities resolved

- 123 test as written; state entries; state 0 closes. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
