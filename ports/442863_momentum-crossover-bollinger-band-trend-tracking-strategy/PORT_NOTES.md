# #442863 Momentum Crossover Bollinger Band Trend Tracking Strategy -> `fmz_442863_seaside_hull_cross_score_flat_entries`

- FMZ source id: 442863 (lineage).
- Source: https://www.fmz.com/strategy/442863 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-26 16:52:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C162). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Hull line crossings with a cross score |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`keh` [10, 20]: **2 trials**.

## Ambiguities resolved

- Entries only from flat. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
