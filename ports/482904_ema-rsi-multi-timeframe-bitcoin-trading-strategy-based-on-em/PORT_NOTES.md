# #482904 基于多重级别EMA与RSI动态势能强度的比特币跨周期趋势交易策略-Multi-Timeframe-Bitcoin-Trading-Strategy-Based-on-EMA-and-RSI-Dynamic-Momentum-Strength -> `fmz_482904_weekly_ema_regime_swing_trail_long`

- FMZ source id: 482904 (lineage).
- Source: https://www.fmz.com/strategy/482904 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:24:26). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; completed weekly values; close-based exits as exit signals. |
| 2 | PASS | EMAs, ATR multiples and rolling extremes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [20, 10] x `atr_len` [5, 14]: **4 trials**; defaults 20 / 5 (the source's); the 7-bar swing, 0.25 / 1.5 /
0.2 / 1 ATR factors fixed; RSI filter off.

## Ambiguities resolved

- `f_sec` on history is `security(...)[1]`: the daily price is the previous close; the weekly EMA 20 is the last
  completed week's (house rule), weeks of broker days from the port's own bars.
- The ratcheting trail and the weekly-EMA exit act through `strategy.close` on closes: exit signals at the next open,
  not broker stops (no trailing mark). Entries only from flat; state machine on the position at each close.
- Long only: opposite entries cannot occur. Broker days stamped with their first minute (as #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`none`
