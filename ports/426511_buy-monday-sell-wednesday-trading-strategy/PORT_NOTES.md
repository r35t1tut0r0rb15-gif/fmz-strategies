# #426511 Buy Monday Sell Wednesday Trading Strategy -> `fmz_426511_monday_wednesday_swing`

- Source: https://www.fmz.com/strategy/426511 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-12 16:44:53). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG426511` (Jaccard >= 0.80) with #427270 (DUPLICATE); best Jaccard 0.818 with #427270. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [2.0, 4.0] x `tp_pct` [3.0, 5.0]: **4 trials**, defaults 4 / 3 (the source's).

## Ambiguities resolved

- Weekday and session in UTC (TradingView's Binance time zone; FMZ undocumented: decision owed); in session = bar open in [14:00, 16:01), i.e. the 16:00 bar on 4h.
- `strategy.close(id, isExit)`: second positional argument read as `when` (Pine v5 of 2023).
- Long only; stops on 4h bars: coarse_bar_stop.

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks (2026-10-07)

`coarse_bar_stop`
