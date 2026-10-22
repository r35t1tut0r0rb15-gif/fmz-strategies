# #446440 基于K线蜡烛图的看涨吞没和看跌吞没策略Bullish-and-Bearish-Engulfing-Strategy-Based-on-Candlestick-Patterns -> `fmz_446440_engulfing_one_bar_hold_reversal`

- FMZ source id: 446440 (lineage).
- Source: https://www.fmz.com/strategy/446440 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-28 16:40:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C174). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Engulfing patterns with a one-bar hold |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written.

## Ambiguities resolved

- Every held position closes at the next bar close. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
