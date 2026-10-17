# #433097 Quantitative Investment Strategy Based on Monthly Buy Date -> `fmz_433097_day_of_month_long`

- FMZ source id: 433097 (lineage).
- Source: https://www.fmz.com/strategy/433097 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-24 14:10:23). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C58). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; calendar-day entries and exits |
| 2 | PASS | Calendar days only |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`entry_day` [26, 20] x `use_exit` [False, True]: **4 trials**; exit day 6 fixed.

## Ambiguities resolved

- Default is buy and hold from the first entry day (use_exit False), as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`
