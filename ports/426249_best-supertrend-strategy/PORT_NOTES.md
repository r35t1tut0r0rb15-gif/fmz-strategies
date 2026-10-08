# #426249 BEST Supertrend Strategy -> `fmz_426249_sma_cross_daily_supertrend`

- Source: https://www.fmz.com/strategy/426249 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-09 22:20:09). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A19). Not run.

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

`factor` [2.0, 3.0] (default 3, header args 2) x `fast` [5, 7] x `slow` [20, 30] = **8 trials**. ST period 3 and the daily timeframe stay at the originals.

## Ambiguities resolved

- Daily SuperTrend on broker days built from the 2 h bars (bar assigned by its open), read as the last completed day ([1], lookahead on).
- Net change per bar emitted (short entry + long close = short); same-side entries ignored.
- `FREQ = "2h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks (2026-10-07)

`none`
