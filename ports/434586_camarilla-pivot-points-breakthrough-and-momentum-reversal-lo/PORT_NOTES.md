# #434586 Camarilla Pivot Points Breakthrough and Momentum Reversal Low Absorption Golden Cross Strategy -> `fmz_434586_camarilla_r1_s1_side`

- FMZ source id: 434586 (lineage).
- Source: https://www.fmz.com/strategy/434586 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-07 16:57:11). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C69). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed broker days |
| 2 | PASS | Prior-day range levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`level` [1, 2] x `reverse` [False, True]: **4 trials**; `level` 1 = R1 / S1 (R / 12), 2 = R2 / S2 (R / 6).

## Ambiguities resolved

- Last completed broker day's Camarilla levels. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
