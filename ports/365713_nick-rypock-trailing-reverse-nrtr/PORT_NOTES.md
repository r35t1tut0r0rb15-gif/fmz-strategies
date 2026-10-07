# #365713 Nick Rypock Trailing Reverse -> `fmz_365713_nrtr_close_reverse`

- Source: https://www.fmz.com/strategy/365713 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-25 18:14:32). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A13). Not run.

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

`k_pct` [1.0, 2.0, 3.0, 5.0] % = **4 trials**.

## Ambiguities resolved

- The reverse level is the entry signal (always-in reversal on closes), not a protective stop.
- trend starts 0 (treated as up); a 0 -> -1 change is not an entry (needs trend[1] == 1).
- `FREQ = "2h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks (2026-10-07)

`none`
