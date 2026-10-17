# #488275 Black-Scholes波动率自适应突破策略与动态阈值优化-Black-Scholes-Volatility-Adjusted-Breakout-with-Dynamic-Threshold-Optimization -> `fmz_488275_expected_move_breakout`

- FMZ source id: 488275 (lineage).
- Source: https://www.fmz.com/strategy/488275 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 14:34:45). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail pending (mark). |
| 2 | PASS | A volatility-scaled threshold and a moving average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 5 / pyramiding 5 quoted; the trail quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vol_lookback` [20, 40] x `ma_length` [20, 50]: **4 trials**; defaults 20 / 20 (the source's); the MA filter on.

## Trailing stop (rule 2, mark `trailing_stop_pending`)

As written, every bar in a position: `strategy.exit(trail_points = trail_offset = expectedMove x 1.0)`, a price
distance in tick arguments (read as a price distance, #427592), equal to close[1] x the 20-bar standard deviation of
log returns, re-issued every bar. A volatility measure other than ATR with a moving activation: not expressible in
the house trail, not emitted. The 1 % / 2 % bracket applies only when the trail is switched off (not the default):
not ported.

## Ambiguities resolved

- sqrt(ppy) cancels, so `chartRes` has no effect. Adds (pyramiding 5) are sizing: net position only (#490570).
  REVERSAL INTENDED. Daily bars are broker days; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_breakout"`.

## Marks

`trailing_stop_pending`
