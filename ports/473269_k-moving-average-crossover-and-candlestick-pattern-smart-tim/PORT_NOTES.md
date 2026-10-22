# #473269 均线交叉趋势捕捉与K线突破智能择时策略-Moving-Average-Crossover-and-Candlestick-Pattern-Smart-Timing-Strategy -> `fmz_473269_sma14_28_cross_reversal`

- FMZ source id: 473269 (lineage).
- Source: https://www.fmz.com/strategy/473269 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 17:18:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C216). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Margin settings only. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (the SMA lengths are constants; the wick inputs feed no order).

## Ambiguities resolved

- The wick-reversal block feeds no order (as written). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
