# #474885 Price Pattern Based Double Bottom and Top Automated Trading Strategy -> `fmz_474885_exact_double_bottom_top_100bar_reversal`

- FMZ source id: 474885 (lineage).
- Source: https://www.fmz.com/strategy/474885 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 17:29:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C226). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Exact double bottoms / tops |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Fixed qty 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 50]: **2 trials**; lookback equal to the length.

## Ambiguities resolved

- The close tests never hold (as written). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
