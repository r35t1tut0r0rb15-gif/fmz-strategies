# #426854 Quantitative Momentum Trend Trading Strategy -> `fmz_426854_quantcat_momentum`

- Source: https://www.fmz.com/strategy/426854 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-14 20:38:49). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A27). Not run.

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

`stop_mult` [0.6, 1.0] x `target_mult` [1.5, 2.2] x `lookback` [40, 60]: **8 trials**, defaults 0.6 / 2.2 / 60 (the source's); EMAs 20 / 40 / 60, max crosses 2, RSI and MACD levels fixed.

## Ambiguities resolved

- Daily ATR on broker days from the hourly bars; lookahead_off shows the last completed day.
- Stops are daily-ATR multiples from the signal close, applied to the fill.
- As written the 40-EMA bear test compares with the 60-EMA crossover sum (kept).
- MACD thresholds +-0.5 are price units (0 ATR on BTC), kept.
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks (2026-10-07)

`none`
