# #362649 Rolling Heikin Ashi Candles -> `fmz_362649_rolling_heikin_ashi_inverse`

- Source: https://www.fmz.com/strategy/362649 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-12 16:42:15). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A8). Not run.

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

`tf` [3, 5, 8] = **3 trials**.

## Ambiguities resolved

- Red rolling candle (haopen > haclose) enters long, green enters short: inverted relative to the colour, kept as written.
- The recursion on `haopen[2*tf-1]` uses the reassigned history, as Pine does.
- `FREQ = "6h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi_trend"`.

## Marks (2026-10-07)

`none`
