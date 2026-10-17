# #483020 动量背离趋势反转量化策略基于MACD柱状图-Momentum-Divergence-Trend-Reversal-Quantitative-Strategy-Based-on-MACD-Histogram -> `fmz_483020_macd_hist_fade_big_candle_reversal`

- FMZ source id: 483020 (lineage).
- Source: https://www.fmz.com/strategy/483020 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 09:25:50). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MACD histogram and candle bodies. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 21]: **4 trials**; defaults 12 / 26 (the source's); signal 9 fixed.

## Ambiguities resolved

- The closes on the opposite signal are redundant with the reversing entries. REVERSAL INTENDED; no stops.
  FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`none`
