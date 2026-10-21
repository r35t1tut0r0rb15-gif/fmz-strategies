# #438807 IBS and Weekly High Based SP500 Futures Trading Strategy -> `fmz_438807_monday_ibs_weekly_close_long`

- FMZ source id: 438807 (lineage).
- Source: https://www.fmz.com/strategy/438807 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-15 14:42:00). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C113). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly value from completed weeks |
| 2 | PASS | Weekday, IBS and close tests |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ibs_max` [0.5, 0.3] x `hold_bars` [4, 8]: **4 trials**.

## Ambiguities resolved

- Weekly close two broker weeks back; the 4-bar exit counts hours. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`
