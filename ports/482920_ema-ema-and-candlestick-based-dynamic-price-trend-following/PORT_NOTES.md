# #482920 基于EMA和蜡烛图的动态价格跟踪趋势交易策略-EMA-and-Candlestick-Based-Dynamic-Price-Trend-Following-Strategy -> `fmz_482920_pin_engulf_ema_trend_reversal`

- FMZ source id: 482920 (lineage).
- Source: https://www.fmz.com/strategy/482920 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 17:43:21). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Candle shapes and moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 12] x `slow` [21, 50]: **4 trials**; defaults 8 / 21 (the source's).

## Ambiguities resolved

- "bearish" trend is EMA 8 not above EMA 21, as written (the ternary). The ATR is unused.
- REVERSAL INTENDED; no exits or stops. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick"`.

## Marks

`none`
