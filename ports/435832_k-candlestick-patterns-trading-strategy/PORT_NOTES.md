# #435832 形态K线交易策略Candlestick-Patterns-Trading-Strategy -> `fmz_435832_candlestick_pattern_signals_long`

- FMZ source id: 435832 (lineage).
- Source: https://www.fmz.com/strategy/435832 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-19 10:56:36). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C82). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle shape comparisons |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity-based order size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

no searched parameter: **1 trial**.

## Ambiguities resolved

- Entry and a close pattern on one bar: flat. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
