# #434336 Average Highest High and Lowest Low Swinger Strategy -> `fmz_434336_avg_hh_ll_swinger`

- FMZ source id: 434336 (lineage).
- Source: https://www.fmz.com/strategy/434336 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-05 16:34:01). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C66). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel midpoints |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 20] x `slow` [26, 52]: **4 trials**.

## Ambiguities resolved

- Windows include the current bar. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
