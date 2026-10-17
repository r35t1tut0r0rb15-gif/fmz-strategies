# #482902 综合K线图形态与趋势线技术分析策略-Comprehensive-Candlestick-and-Trendline-Pattern-Analysis-Strategy -> `fmz_482902_candle_pattern_basket_reversal`

- FMZ source id: 482902 (lineage).
- Source: https://www.fmz.com/strategy/482902 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:25:51). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Candle shapes; the price-unit exits are inert and dropped. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the inert exits quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`GRID = {}`: **1 trial**; the source has no inputs.

## Ambiguities resolved

- The patterns are literal, including the hammer's 0.001 price-unit guard.
- The 10-point stop / target are price units: on DOGE_USDT (price about 0.25) the long stop is below zero and the
  target out of reach; dropped as inert (as #492009, #490798).
- REVERSAL INTENDED; with both pattern groups on one bar the later short wins. No exits or stops. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick"`.

## Marks

`none`
