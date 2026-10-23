# #483935 多指标合成多维决策交易系统-基于RSIMACD布林带成交量及趋势的量化策略-Multi-Indicator-Composite-Multi-Dimensional-Decision-Trading-System-A-Quantitative-Strategy-Based-on-RSI-MACD-Bollinger-Bands-Volume-and-Trend -> `fmz_483935_five_indicator_vote_3of5_2h_reversal`

- FMZ source id: 483935 (lineage).
- Source: https://www.fmz.com/strategy/483935 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 09:41:04). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Five-indicator vote |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 15 % of equity and commission stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`need` [3, 4] x `rsi_len` [18, 14]: **4 trials**; MACD 12 / 26 / 9, BB 20 x 2.5, SMA 50, volume SMA 20.

## Ambiguities resolved

- Votes are states. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "indicator_vote"`.

## Marks

`none`
