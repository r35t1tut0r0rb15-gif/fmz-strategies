# #428855 Reversal Prediction and Oscillator Combo Strategy -> `fmz_428855_combo_123_cfo`

- FMZ source id: 428855 (lineage).
- Source: https://www.fmz.com/strategy/428855 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-10 10:39:44). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels and a percentage only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_cfo` [14, 28]: **4 trials**; K smoothing 1, D 3, level 50, offset 0 fixed.

## Ambiguities resolved

- Disagreement closes all. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
