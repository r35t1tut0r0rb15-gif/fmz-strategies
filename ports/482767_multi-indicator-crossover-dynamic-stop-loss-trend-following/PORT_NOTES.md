# #482767 多指标交叉动态止盈止损趋势跟踪策略-Multi-Indicator-Crossover-Dynamic-Stop-Loss-Trend-Following-Strategy -> `fmz_482767_ema8_21_cross_adx_macd_rsi_atr_bracket_trail_long`

- FMZ source id: 482767 (lineage).
- Source: https://www.fmz.com/strategy/482767 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:52:08). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the bracket and trail set at entry. |
| 2 | PASS | EMAs, ADX, MACD, RSI and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity; the commission is a cost; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [1.5, 2.5] x `tp_mult` [2.0, 3.0]: **4 trials**; defaults 1.5 / 2 (the source's); EMA 8 / 21, RSI 14 < 70,
ADX 14 > 25, MACD 12 / 26 / 9 and the trail (0.3 ATR after about 2 %) fixed.

## Trailing stop (mark `trailing_stop`)

`trail_points = 0.5 ATR`, `trail_offset = 0.3 ATR`: price distances given to tick arguments, read as price
distances (#427592). House trail `{"type": "volatility", "atr_n": 14, "k": 0.3, "anchor": "high_low",
"activate_after": 0.02}`: the 0.5 ATR activation as a fraction judged on ETH_USDT daily bars (ATR about 4 % of the
price; as #428795).

## Ambiguities resolved

- DI / ADX as written (RMA of `ta.tr(true)`, no fixnan). Long only. Stop module: `portfolio_kwargs` {} (D4).
  Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`, `trailing_stop`
