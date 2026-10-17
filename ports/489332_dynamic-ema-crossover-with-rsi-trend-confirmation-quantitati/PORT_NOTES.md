# #489332 动态均线交叉结合超买超卖趋势确认量化交易策略-Dynamic-EMA-Crossover-with-RSI-Trend-Confirmation-Quantitative-Trading-Strategy -> `fmz_489332_ema_50_200_cross_rsi_tick_bracket`

- FMZ source id: 489332 (lineage).
- Source: https://www.fmz.com/strategy/489332 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-03 15:05:58). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | ADAPT | 50 / 100 ticks -> `sl_atr` x ATR(14) and 2 x that. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.0125, 1.0] x `tp_ratio` [2.0, 4.0]: **4 trials**; defaults 0.0125 / 2 (the source's equivalents); EMA
50 / 200 and RSI 14 fixed. On hourly BTC_USDT 50 ticks of 0.1 are 5 USD, about 0.0125 ATR (judgement, stated before
any backtest).

## Ambiguities resolved

- The short reuses the long's stop (below the price) and limit (above it): it is closed on its own fill. Its only
  lasting effect is closing a long, so the short signal is ported as a long exit (no zero-length short).
- Long only in effect. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
