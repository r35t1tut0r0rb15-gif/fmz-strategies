# #483072 动态波动率止损的趋势动量交易策略-Dynamic-Volatility-Based-Stop-Loss-Trend-Momentum-Trading-Strategy -> `fmz_483072_macd_cross_ema20_long_atr_ratchet`

- FMZ source id: 483072 (lineage).
- Source: https://www.fmz.com/strategy/483072 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 11:39:56). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the ratchet fixed at entry (marked). |
| 2 | PASS | MACD, an EMA and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the stop via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_mult` [2.0, 3.0] x `ema_len` [20, 50]: **4 trials**; defaults 2 / 20 (the source's); MACD 12 / 26 / 9 and ATR
14 fixed.

## Trailing stop (mark `trailing_stop_pending`)

While held, `trailing = max(trailing, close - 2 ATR)` and the exit stop is that level (the 1 ATR stop is overwritten
before it is ever placed). A ratchet on closes minus each bar's own ATR is not the house volatility trail (best price
minus the current ATR, which may retreat), so the port fixes 2 ATR / close of the signal bar at entry.

## Ambiguities resolved

- The sell close is an exit signal. Long only: opposite entries cannot occur. Stop module: `portfolio_kwargs` {} (D4).
- Stops on 2-hour bars: `coarse_bar_stop`. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
