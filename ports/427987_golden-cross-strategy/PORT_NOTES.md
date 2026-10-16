# #427987 Golden Cross Strategy -> `fmz_427987_golden_cross_long`

- FMZ source id: 427987 (lineage).
- Source: https://www.fmz.com/strategy/427987 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-27 16:23:51). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`l_short` [50, 20] x `l_long` [200, 100]: **4 trials**; defaults 50 / 200 (the source's).

## Ambiguities resolved

- testPeriod() is true. Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
