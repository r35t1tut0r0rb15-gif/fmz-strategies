# #440986 基于SMA和滚动趋势线的量化交易策略Quantitative-Trading-Strategy-Based-on-SMA-and-Rolling-Trendline -> `fmz_440986_sma14_rolling_trendline_long`

- FMZ source id: 440986 (lineage).
- Source: https://www.fmz.com/strategy/440986 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-04 15:18:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C143). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA side and rolling regression value |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_period` [14, 28] x `window` [20, 40]: **4 trials**.

## Ambiguities resolved

- Trendline value at the window's oldest bar, as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
