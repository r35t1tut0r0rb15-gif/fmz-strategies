# #426779 Mechanical Trading Strategy -> `fmz_426779_daily_1600_long_bracket`

- Source: https://www.fmz.com/strategy/426779 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-14 15:19:05). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [0.4, 1.0] x `sl_pct` [0.2, 0.5]: **4 trials**, defaults 0.4 / 0.2 (the source's).

## Ambiguities resolved

- Hour read in UTC (decision owed); the 16:00 bar on 4h.
- Bracket from the signal close applied to the fill; re-issued at later 16:00 bars while long (moving level): trailing_stop_pending.
- Long only; stops on 4h bars: coarse_bar_stop.

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks (2026-10-07)

`trailing_stop_pending, coarse_bar_stop`
