# #486573 多指标趋势确认交易系统-均线融合RSI背离MACD信号策略-Multi-Indicator-Trend-Confirmation-Trading-System-EMA-Confluence-with-RSI-Divergence-and-MACD-Signal-Strategy -> `fmz_486573_close_ema50_cross_ema_stack_rsi_macd_reversal`

- FMZ source id: 486573 (lineage).
- Source: https://www.fmz.com/strategy/486573 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-14 09:52:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C264). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA-stack crossings with RSI and MACD confirmation |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG486573. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [50, 20] x `len3` [200, 150]: **4 trials**; EMA 100, RSI 14, MACD 12 / 26 / 9.

## Ambiguities resolved

- No exits; REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
