# #448076 SPARK动态仓位与双重指标交易策略-SPARK-Dynamic-Position-Sizing-and-Dual-Indicator-Trading-Strategy -> `fmz_448076_four_trendflow_rsi_extreme_gated_reversal`

- FMZ source id: 448076 (lineage).
- Source: https://www.fmz.com/strategy/448076 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-04-12 17:22:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C178). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving brackets not ported (mark) |
| 2 | PASS | SuperTrend agreement and RSI extremes with a bars-since gate |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The portfolio share, leverage and percent levels stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`min_bars` [5, 10] x `rsi_len` [14, 7]: **4 trials**; the four trend-flow settings and the RSI levels fixed.

## Ambiguities resolved

- All-down short never passes its gate; brackets pending. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`trailing_stop_pending`
