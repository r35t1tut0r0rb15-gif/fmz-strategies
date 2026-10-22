# #471671 结合布林带与RSI的自适应震荡趋势交易策略-Adaptive-Oscillation-Trend-Trading-Strategy-with-Bollinger-Bands-and-RSI-Integration -> `fmz_471671_alternating_macd_cross_band_edges_bar_gap_reversal`

- FMZ source id: 471671 (lineage).
- Source: https://www.fmz.com/strategy/471671 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 11:35:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C209). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings at the band edges, alternating with a bar gap |
| 3 | PASS | Exchange pair in the header only (ETH named in the title). |
| 4 | DONE | Fixed trade size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`min_gap` [15, 5] x `bb_length` [20, 50]: **4 trials**; the RSI levels fixed.

## Ambiguities resolved

- First trade a long, sides alternate (as written). REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
