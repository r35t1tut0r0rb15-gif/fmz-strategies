# #486573 多指标趋势确认交易系统-均线融合RSI背离MACD信号策略-Multi-Indicator-Trend-Confirmation-Trading-System-EMA-Confluence-with-RSI-Divergence-and-MACD-Signal-Strategy -> `fmz_486573_ema_stack_reclaim_rsi_macd`

- FMZ source id: 486573 (lineage).
- Source: https://www.fmz.com/strategy/486573 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-14 09:52:05). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMAs and oscillators. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | `DG486573` with #489201 (Jaccard 1.000; #489201 is DUPLICATE in screening): this member ported. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [50, 20] x `rsi_ob` [70, 80]: **4 trials**; defaults 50 / 70 (the source's); EMA 100 / 200, RSI 14 (oversold
30) and MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- The Bollinger bands are computed but unused. No exit other than the opposite entry: REVERSAL INTENDED. Daily bars
  are broker days; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_filter"`.

## Marks

`none`
