# #429498 Tracking Breakout Strategy -> `fmz_429498_donchian_after_opposite_touch`

- FMZ source id: 429498 (lineage).
- Source: https://www.fmz.com/strategy/429498 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-17 16:36:49). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | PASS | Channel levels and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy() cash quantity stored; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `riskreward` [1.5, 3.0]: **4 trials**; EMA 200 and the 0.5 % pullbacks fixed.

## Ambiguities resolved

- Flat and flag resets tracked through the bracket. Mark coarse_bar_stop. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`coarse_bar_stop`
