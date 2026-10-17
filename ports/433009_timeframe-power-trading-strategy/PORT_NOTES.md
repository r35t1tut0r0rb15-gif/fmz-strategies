# #433009 Timeframe Power Trading Strategy -> `fmz_433009_time_of_day_long`

- FMZ source id: 433009 (lineage).
- Source: https://www.fmz.com/strategy/433009 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-23 15:32:00). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C56). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; clock-time entries and exits |
| 2 | PASS | Clock times only |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tz` ["UTC", "America/New_York"] x `exit_hour` [2, 3]: **4 trials**; entry hour 0 fixed (the default slots).

## Ambiguities resolved

- Exchange clock in UTC (header) or New York, both declared; the tested times, not the labels. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`
