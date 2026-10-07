# #362059 Best-TradingView-Strategy -> `fmz_362059_sma_trend_bb_lower_cross`

- Source: https://www.fmz.com/strategy/362059 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-09 21:42:21). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close entries. |
| 2 | PASS (trail pending) | Tick-based trail -> to be re-expressed in ATR when the trail is decided. |
| 3 | PASS | Bitfinex spot pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | The name's claim is not used. |

## Declared grid (criterion 5)

`bb_len` [15, 20] x `bb_mult` [2, 2.5] x `slow_sma` [42, 84] = **8 trials**.

## Ambiguities resolved

- **Trailing stop pending (rule 2)**: `strategy.exit(trail_points=100, trail_offset=50)` (ticks) is created on the bar where SMA42 crosses above SMA14 (long; mirror for short) and stays active: once price is 100 ticks in profit, a stop trails 50 ticks behind the best price. In the port these become ATR multiples once the project decides how trails are expressed.
- The short entry also uses the LOWER band (crossunder), as written.
- `FREQ = "15min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks (2026-10-07)

`trailing_stop_pending`
