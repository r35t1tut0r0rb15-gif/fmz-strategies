# #434470 Auto S R Breakout Strategy -> `fmz_434470_pivot_sr_cross`

- FMZ source id: 434470 (lineage).
- Source: https://www.fmz.com/strategy/434470 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-06 16:51:30). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C67). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Price against its own pivot levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`left` [50, 20] x `right` [5, 3]: **4 trials**.

## Ambiguities resolved

- Strict pivots on closes, levels from the pivot bar's high / low; unused 25-bar pivots dropped. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks

`none`
