# #367476 Linear trend -> `fmz_367476_linreg_channel_trend`

- Source: https://www.fmz.com/strategy/367476 (PineScript v4, author Zer3192, FMZ last
  modified 2022-06-03 16:09:05). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND362178` (Jaccard 0.65-0.80) with #362178 (PORT_CANDIDATE); best Jaccard 0.704 with #362178. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 200] x `dev` [2.0, 3.0, 4.0] = **6 trials**.

## Ambiguities resolved

- Channel as #365345; lines ratchet with close[1] like a SuperTrend.
- trend starts 1.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks (2026-10-07)

`none`
