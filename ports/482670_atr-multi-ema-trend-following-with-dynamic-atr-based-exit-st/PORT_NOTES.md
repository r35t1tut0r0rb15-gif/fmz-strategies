# #482670 基于多均线趋势和ATR动态止盈止损的加密货币交易策略-Multi-EMA-Trend-Following-with-Dynamic-ATR-Based-Exit-Strategy-for-Cryptocurrency-Trading -> `fmz_482670_ema9_20_cross_trend_distance_daily_one_atr_bracket`

- FMZ source id: 482670 (lineage).
- Source: https://www.fmz.com/strategy/482670 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 14:45:33). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | EMAs, RSI and ATR multiples; the price-level slope filters are inert and dropped. |
| 3 | PASS | No exchange in the header. |
| 4 | DONE | 2 % of equity and the risk sizing quoted; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [2.5, 3.0] x `tp_mult` [3.5, 4.0]: **4 trials**; defaults 2.5 / 3.5 (the source's default row); EMA
9 / 20 / 50, RSI 14, ATR 14 and the 1.1 ATR distance fixed. The per-ticker table (EURUSD 3.0 / 3.8, USDJPY 2.5 / 3.5,
GBPUSD 3.0 / 4.0, AUDUSD 3.2 / 4.0, GBPJPY 3.0 / 5.0) is not looked up by symbol.

## Ambiguities resolved

- `ta.linreg(refEMA, 5, 0) > -0.2` / `< 0.2` compare a price with constants: always true / never true above 0.2, so
  both are dropped as inert (as #492009) and the port is long only.
- Clock rule (check 9 / C6): the daily counter resets on a new UTC day (no exchange named); it counts signals.
- `bar_index > 10` kept. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
