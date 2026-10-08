# #380219 Candle Strength -> `fmz_380219_candle_colour_follow`

- Source: https://www.fmz.com/strategy/380219 (PineScript v5, author Zer3192, FMZ last
  modified 2022-08-27 12:03:45). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A17). Not run.

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

No parameters: **1 trial**, the source as written.

## Ambiguities resolved

- Odd indentation of the entry lines read as their if/else-if blocks (as the FMZ runtime runs them).
- Percent labels only draw.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks (2026-10-07)

`none`
