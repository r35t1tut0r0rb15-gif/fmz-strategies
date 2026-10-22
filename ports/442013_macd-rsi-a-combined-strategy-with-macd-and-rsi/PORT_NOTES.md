# #442013 基于MACD与RSI组合策略A-Combined-Strategy-with-MACD-and-RSI -> `fmz_442013_macd5_35_cross_rsi_filter_long`

- FMZ source id: 442013 (lineage).
- Source: https://www.fmz.com/strategy/442013 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-18 16:07:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C150). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings with RSI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_length` [5, 12] x `slow_length` [35, 26]: **4 trials**; signal 5 and RSI levels fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
