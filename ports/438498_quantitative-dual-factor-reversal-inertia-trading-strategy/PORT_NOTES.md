# #438498 Quantitative Dual Factor Reversal Inertia Trading Strategy -> `fmz_438498_reversal123_inertia_combo`

- FMZ source id: 438498 (lineage).
- Source: https://www.fmz.com/strategy/438498 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-12 14:38:02). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C111). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and relative volatility |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426322. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `period` [10, 20]: **4 trials**; K smoothing 1, D 3, level 50 and smooth 14 fixed.

## Ambiguities resolved

- 123 test as written; disagreement closes. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
