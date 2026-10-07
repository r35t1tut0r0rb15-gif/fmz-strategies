# #365315 Quantitative Qualitative Estimation -> `fmz_365315_qqe_fast_slow_cross`

- Source: https://www.fmz.com/strategy/365315 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-24 11:28:43). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A12). Not run.

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

`rsi_len` [9, 14, 21] x `sf` [3, 5, 8] = **9 trials**. Factor 4.236 stays at the original.

## Ambiguities resolved

- nz() seeds kept: the two Wilder averages start from 0; QQES recursion as coded (line 91).
- "Show Crossing Signals" default true gates the orders.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
