# #427884 Reversal and Linear Regression Intercept Combo Strategy -> `fmz_427884_combo_123_reversal_lri`

- FMZ source id: 427884 (lineage).
- Source: https://www.fmz.com/strategy/427884 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-26 15:56:48). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels and regression lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21] x `length_lri` [14, 28]: **4 trials**; defaults 14 / 14 (the source's); K 1, D 3, level 50 fixed.

## Ambiguities resolved

- LRI formula as written (i counts bars back; the intercept is the current bar's value).
- "Trade reverse" fixed off. Disagreement closes the position. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
