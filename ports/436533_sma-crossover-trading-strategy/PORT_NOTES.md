# #436533 SMA Crossover Trading Strategy -> `fmz_436533_open_sma_cross_reversal`

- FMZ source id: 436533 (lineage).
- Source: https://www.fmz.com/strategy/436533 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-25 16:03:48). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C91). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [36, 20] x `slow` [46, 60]: **4 trials**; both sources are the open.

## Ambiguities resolved

- Long on the slow crossing over the fast, as written; date window treated as true. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
