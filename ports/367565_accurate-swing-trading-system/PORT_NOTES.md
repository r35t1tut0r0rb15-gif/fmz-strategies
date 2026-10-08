# #367565 Accurate Swing Trading System -> `fmz_367565_swing_stop_line_cross`

- Source: https://www.fmz.com/strategy/367565 (PineScript v4, author Zer3192, FMZ last
  modified 2022-06-04 07:05:48). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A15). Not run.

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

`swing` [2, 3, 5, 8] = **4 trials**.

## Ambiguities resolved

- avn = last non-zero breakout direction (valuewhen); 0 before the first (tsl = res then).
- Colour options only draw.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks (2026-10-07)

`none`
