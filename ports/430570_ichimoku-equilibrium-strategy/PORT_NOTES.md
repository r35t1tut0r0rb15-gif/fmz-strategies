# #430570 Ichimoku Equilibrium Strategy -> `fmz_430570_ichimoku2c`

- FMZ source id: 430570 (lineage).
- Source: https://www.fmz.com/strategy/430570 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-30 14:45:40). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Channel midpoints. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`span` [52, 26] x `displacement` [26, 13]: **4 trials**; conversion 9 and base 26 fixed.

## Ambiguities resolved

- Span names as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
