# #483037 多重指标趋势跟踪策略基于SMA双线交叉结合RSI和ADX的动态波动率优化系统-Multi-Indicator-Trend-Following-Strategy-SMA-Dual-Line-Crossover-with-RSI-and-ADX-Dynamic-Volatility-Optimization-System -> `fmz_483037_sma10_200_rsi_adx_tick_trail`

- FMZ source id: 483037 (lineage).
- Source: https://www.fmz.com/strategy/483037 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:15:22). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close entries; the trail a house trail (approximation stated). |
| 2 | PASS | Moving averages, RSI, ADX; tick distances as ATR / price fractions. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 2 % of equity quoted; the trail via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_k` [0.014, 1.0] x `fast` [10, 20]: **4 trials**; defaults 0.014 / 10 (the source as written); SMA 200, RSI 14,
DMI 14 / 14, ADX > 20 and the activation 0.00011 fixed.

## Trailing stop (mark `trailing_stop`)

`trail_points = 30`, `trail_offset = 5` are literal ticks: on ETH_USDT (mintick 0.01) the trail starts 0.30 USD in
profit and trails 0.05 USD behind the best price; with a 4-minute ATR of about 3.5 USD and price about 2,700 USD that is
the house trail `{"type": "volatility", "atr_n": 14, "k": 0.014, "anchor": "high_low", "activate_after": 0.00011}`
(as #428795). Promotion of a trailing trial needs the cTrader check (gate `trailing_ctrader_check`).

## Ambiguities resolved

- REVERSAL INTENDED. ADX as `ta.dmi` (as #426579). Stop module: `portfolio_kwargs` {} (D4). FREQ = "4min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop`
