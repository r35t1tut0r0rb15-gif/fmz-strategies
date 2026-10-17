# #432883 123 Reversal Moving Average Convergence Divergence Combination Strategy -> `fmz_432883_combo_123_kst`

- FMZ source id: 432883 (lineage).
- Source: https://www.fmz.com/strategy/432883 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-22 14:49:41). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C54). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and rate-of-change sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `level` [50, 40]: **4 trials**; K smoothing 1, D 3 and the KST lengths fixed.

## Ambiguities resolved

- Combined state acted on every bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
