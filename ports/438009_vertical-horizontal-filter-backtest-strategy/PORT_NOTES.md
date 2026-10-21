# #438009 Vertical Horizontal Filter Backtest Strategy -> `fmz_438009_vhf_level_state`

- FMZ source id: 438009 (lineage).
- Source: https://www.fmz.com/strategy/438009 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-08 10:20:25). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C107). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | VHF level |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [28, 14] x `signal` [0.4, 0.3]: **4 trials**; reverse off.

## Ambiguities resolved

- Level-state entries; long in trend, short in congestion as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
