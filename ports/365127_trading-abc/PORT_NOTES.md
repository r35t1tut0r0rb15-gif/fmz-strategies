# #365127 Trading ABC -> `fmz_365127_trading_abc_pullback`

- Source: https://www.fmz.com/strategy/365127 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-24 10:13:47). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`prd` [5, 8, 13] x `error_rate` [0.05, 0.10] = **6 trials**. Fibonacci 0.382/0.618, six-bar window and the six MAs stay at the originals.

## Ambiguities resolved

- `highestbars(high, 8) == 0` read as high equal to the 8-bar high (ties to the current bar); array.max/min of the MAs ignore MAs not yet defined.
- Labels, lines and the stochastic do not reach the orders.
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks (2026-10-07)

`none`
