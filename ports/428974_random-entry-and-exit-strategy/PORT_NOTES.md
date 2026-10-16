# #428974 Random Entry and Exit Strategy -> `fmz_428974_random_entries_long`

- FMZ source id: 428974 (lineage).
- Source: https://www.fmz.com/strategy/428974 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-11 15:17:28). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; a seeded draw per bar. |
| 2 | PASS | No price units. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`seed` [1, 2] x `exit_frequency` [3, 1]: **4 trials**; enter 10 % fixed.

## Ambiguities resolved

- Unseeded random() -> a declared seed (reproducible). Inputs' default direction (Long Only), not the header args.
- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "random_benchmark"`.

## Marks

`none`
