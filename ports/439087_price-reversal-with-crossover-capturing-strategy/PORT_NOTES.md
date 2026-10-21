# #439087 Price Reversal with Crossover Capturing Strategy -> `fmz_439087_reversal123_stoch_cross_combo`

- FMZ source id: 439087 (lineage).
- Source: https://www.fmz.com/strategy/439087 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-17 16:29:13). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C116). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns and stochastic states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_sc` [7, 14]: **4 trials**; K smoothing 1, D 3, level 50 and the 20 / 70 levels fixed.

## Ambiguities resolved

- States as written; disagreement closes. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
