# #438951 Combination Strategy of 123 Reversal and Pivot Point -> `fmz_438951_reversal123_daily_pivot_combo`

- FMZ source id: 438951 (lineage).
- Source: https://www.fmz.com/strategy/438951 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-16 15:48:44). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C114). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily levels from completed days |
| 2 | PASS | Close patterns, stochastic and floor pivots |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `level_set` [1, 2]: **4 trials**; level set 1 = R1 / S1, 2 = R2 / S2; K smoothing 1, D 3, level 50 fixed.

## Ambiguities resolved

- Daily pivots from the previous broker day; disagreement closes. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
