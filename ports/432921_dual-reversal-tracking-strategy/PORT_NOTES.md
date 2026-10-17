# #432921 Dual Reversal Tracking Strategy -> `fmz_432921_combo_123_key_reversal_down`

- FMZ source id: 432921 (lineage).
- Source: https://www.fmz.com/strategy/432921 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-22 17:42:23). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C55). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and a bar pattern |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `n_len` [1, 3]: **4 trials**; K smoothing 1, D 3 and level 50 fixed.

## Ambiguities resolved

- The long branch cannot fire as written. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
