# #428582 Combo Strategy with Multiple Indicators -> `fmz_428582_combo_123_reversal_tema`

- FMZ source id: 428582 (lineage).
- Source: https://www.fmz.com/strategy/428582 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-07 10:25:40). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C17). Not run.
- Near-duplicate group: **ND426888** (31 members, best partner #440094, Jaccard 0.657); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels and MA lengths. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21] x `length_tema` [26, 50]: **4 trials**; defaults 14 / 26 (the source's); K 1, D 3, level 50 fixed.

## Ambiguities resolved

- "Trade reverse" fixed off. Disagreement closes the position. REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
