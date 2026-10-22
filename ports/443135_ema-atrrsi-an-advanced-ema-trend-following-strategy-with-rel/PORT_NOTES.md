# #443135 基于EMA和ATRRSI过滤器的趋势跟踪策略An-Advanced-EMA-Trend-Following-Strategy-with-Relaxed-RSI-and-ATR-Filters -> `fmz_443135_ema20_50_cross_ema200_filter_cross_exits`

- FMZ source id: 443135 (lineage).
- Source: https://www.fmz.com/strategy/443135 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-29 14:44:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C167). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with a trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_ema` [20, 10] x `long_ema` [50, 100]: **4 trials**; the trend EMA fixed.

## Ambiguities resolved

- Closes act on held ids. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
