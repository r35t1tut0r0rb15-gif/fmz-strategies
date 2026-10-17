# #434979 52周高低盒子交易策略52-Week-High-Low-Box-Trading-Strategy -> `fmz_434979_darvas_daily_box_hourly`

- FMZ source id: 434979 (lineage).
- Source: https://www.fmz.com/strategy/434979 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-11 14:43:30). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C72). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed broker days |
| 2 | PASS | Box levels from prior-day ranges |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`boxp` [5, 8]: **2 trials**.

## Ambiguities resolved

- Hourly windows over prior-day values, as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
