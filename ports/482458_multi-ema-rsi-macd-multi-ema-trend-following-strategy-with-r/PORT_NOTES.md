# #482458 Multi-EMA趋势追踪型RSI-MACD动量验证策略-Multi-EMA-Trend-Following-Strategy-with-RSI-MACD-Momentum-Validation -> `fmz_482458_ema_stack_macd_zero_cross_rsi50_short_closed_at_fill_reversal`

- FMZ source id: 482458 (lineage).
- Source: https://www.fmz.com/strategy/482458 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 15:13:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C245). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the long's moving stop described (pending) |
| 2 | PASS | EMA stack with MACD zero crossings and RSI side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`macd_fast` [12, 8] x `macd_slow` [26, 21]: **4 trials**; EMA 5 / 14 / 34 / 55, signal 9, RSI 14.

## Ambiguities resolved

- The short's marketable take-profit closes it on the fill bar (one bar late here); the long's EMA 34 stop is pending.
- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
