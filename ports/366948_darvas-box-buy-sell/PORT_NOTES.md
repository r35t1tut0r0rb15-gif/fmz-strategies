# #366948 Darvas Box Buy Sell -> `fmz_366948_darvas_box_break`

- Source: https://www.fmz.com/strategy/366948 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-31 19:31:56). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`boxp` [4, 5, 8, 13] = **4 trials**.

## Ambiguities resolved

- Box fixed when barssince(new high) == boxp - 2 and highest(boxp - 2) < highest(boxp - 1).
- Boxes na until the first forms.
- `FREQ = "45min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks (2026-10-07)

`none`
