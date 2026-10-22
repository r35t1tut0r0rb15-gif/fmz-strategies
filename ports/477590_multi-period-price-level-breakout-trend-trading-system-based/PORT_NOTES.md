# #477590 Multi Period Price Level Breakout Trend Trading System Based on Key Price Levels -> `fmz_477590_premarket_prevday_level_break_dayhl_close_flat_only`

- FMZ source id: 477590 (lineage).
- Source: https://www.fmz.com/strategy/477590 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-06 16:06:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C235). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed broker days |
| 2 | PASS | Pre-market and previous-day level breaks with day-high / low closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pm_end_hour` [9, 7] x `switch_hour` [10, 12]: **4 trials**; pre-market from 16:00.

## Ambiguities resolved

- Hours are UTC bar hours (no DST); daily values from completed broker days; previous-day level switches to two days back after 10:00, as written.
- Entries only from flat. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "support_resistance"`.

## Marks

`none`
