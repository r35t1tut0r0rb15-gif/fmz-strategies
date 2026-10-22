# #477943 双均线RSI趋势发散策略基于指数移动平均和相对强弱的趋势捕捉系统-Dual-EMA-RSI-Divergence-Strategy-A-Trend-Capture-System-Based-on-Exponential-Moving-Average-and-Relative-Strength -> `fmz_477943_ema9_26_order_rsi65_35_reversal`

- FMZ source id: 477943 (lineage).
- Source: https://www.fmz.com/strategy/477943 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-10 15:03:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C236). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA order with RSI thresholds |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_long` [65, 60] x `slow` [26, 50]: **4 trials**; EMA 9, RSI 14, short level 100 - long.

## Ambiguities resolved

- The divergence filters are always false (self-comparisons), as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
