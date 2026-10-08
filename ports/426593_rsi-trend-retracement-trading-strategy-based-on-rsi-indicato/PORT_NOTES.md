# #426593 RSI Trend Retracement Trading Strategy Based on RSI Indicator -> `fmz_426593_rsi2_extremes`

- Source: https://www.fmz.com/strategy/426593 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-13 15:33:26). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`rsi_len` [2, 3] x `extreme` [4, 8] x `take` [20, 30]: **8 trials**, defaults 2 / 4 / 20 (the source's 96 / 4 and 20 / 80).

## Ambiguities resolved

- Same-bar entry and close of the other side: the entry stands (the close then finds nothing).
- Trailing stop pending (rule 2): strategy.exit(trail_price = highest high since the long signal / lowest low since the short signal, trail_offset = 100 ticks). As an ATR multiple the offset would be trail_atr x ATR(14) at the signal bar (100 ticks = 10 USDT on BTC, a small fraction of an hourly ATR). Activation: as soon as price trades at the tracked extreme, i.e. immediately; not emitted until the project decides how to express trailing stops.
- Order quantity (1.5 % of a hard-coded 250) is sizing (original_sizing.txt).
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`trailing_stop_pending`
