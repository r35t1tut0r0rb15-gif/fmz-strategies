# #427930 Day of the Week Custom Trading Strategy -> `fmz_427930_day_of_week_long`

- FMZ source id: 427930 (lineage).
- Source: https://www.fmz.com/strategy/427930 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-26 20:49:44). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C14) AS WRITTEN (shifted day labels). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders on the calendar. |
| 2 | PASS | Weekdays only (generic reading stated). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`start_day` [1, 2] x `n_days` [3, 2]: **4 trials**; defaults 1 / 3 (Pine dayofweek 1-3, the source's defaults as they act).

## Ambiguities resolved

- The setting labels are one day off (`timeframes = [7, 1, ..., 6]`): "monday" acts on dayofweek 1 (Sunday). Ported as it acts.
- Weekday = broker-day date. The setting is compared with the previous BAR's day (generic reading; same on 24/7 data, lets weekday-only instruments trade).
- Date window dropped. Long only. FREQ = "1D".

## Decision owed

Whether the intended set is Monday-Wednesday by label (start_day 2) and whether to keep the previous-bar reading.

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_effect"`.

## Marks

`none`
