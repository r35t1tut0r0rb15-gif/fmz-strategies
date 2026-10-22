# #477606 多周期日线K线形态信号交易策略-Multi-Timeframe-Candlestick-Pattern-Trading-Strategy -> `fmz_477606_outside_engulfing_reversal`

- FMZ source id: 477606 (lineage).
- Source: https://www.fmz.com/strategy/477606 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 16:40:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C236). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Outside engulfing candles |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
