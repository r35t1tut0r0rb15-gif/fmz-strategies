# #426557 RSI Moving Average Bollinger Bands RSI Combo Strategy -> `fmz_426557_ma_bollinger_rsi`

- Source: https://www.fmz.com/strategy/426557 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-13 11:57:39). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A23). Not run.

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

`rsi_len` [6, 14] x `bb_len` [100, 200] x `bb_mult` [2.0, 2.5]: **8 trials**, defaults 6 / 200 / 2.0 (the source's); RSI mid 50 and the 11-bar window fixed.

## Ambiguities resolved

- As written the strategy.close calls name ids no entry uses, so they close nothing (decision owed: likely a slip); positions end at the opposite entry.
- The saved 6 % stops only plot.
- Pine population stdev; MA type SMA.
- FREQ = "30min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks (2026-10-07)

`none`
