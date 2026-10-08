# #426923 London Breakout Day Trading Strategy -> `fmz_426923_london_breakout`

- Source: https://www.fmz.com/strategy/426923 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-15 15:43:04). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A28). Not run.

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

`sl` [0.005, 0.01] x `tp` [0.005, 0.01]: **4 trials**, defaults 0.005 / 0.005 (the source's).

## Ambiguities resolved

- Sessions and weekdays in UTC (decision owed); in session = bar open in the window.
- Bracket re-issued every bar at 0.5 % of the current close (moving level): trailing_stop_pending; port fixes 0.5 % of the fill.
- Risk-based lot is sizing.
- FREQ = "30min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks (2026-10-07)

`trailing_stop_pending`
