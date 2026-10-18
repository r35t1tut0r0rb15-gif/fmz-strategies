# #436623 Dual Factor Combo Reversal and Mass Index Strategy -> `fmz_436623_reversal123_mass_index_combo`

- FMZ source id: 436623 (lineage).
- Source: https://www.fmz.com/strategy/436623 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-26 12:20:57). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C93). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Reversal pattern and Mass Index states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 10] x `trigger` [26.5, 25.0]: **4 trials**; the other lengths and the level 50 fixed.

## Ambiguities resolved

- Component positions are levels; close_all on the neutral state. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_state"`.

## Marks

`none`
