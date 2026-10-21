# #438010 Crude Oil Moving Average Crossover Strategy -> `fmz_438010_sma10_30_cross_close_all`

- FMZ source id: 438010 (lineage).
- Source: https://www.fmz.com/strategy/438010 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-08 10:25:00). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C107). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `slow` [30, 60]: **4 trials**.

## Ambiguities resolved

- close_all after the short entry flattens a long (as #430380). REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
