# #477960 双时间框架趋势反转K线形态量化交易策略-Dual-Timeframe-Trend-Reversal-Candlestick-Pattern-Quantitative-Trading-Strategy -> `fmz_477960_hammer_shape_colour_hold26_reversal`

- FMZ source id: 477960 (lineage).
- Source: https://www.fmz.com/strategy/477960 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-10 15:47:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C237). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Hammer-shaped candles with a fixed holding time |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hold_periods` [26, 12] x `length` [5, 3]: **4 trials**; shadow ratio 1.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
