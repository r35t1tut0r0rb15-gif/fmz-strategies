# #473154 多周期趋势跟踪与ATR波动率管理策略-Multi-Timeframe-Trend-Following-Strategy-with-ATR-Volatility-Management -> `fmz_473154_ema9_21_cross_rsi_filter_shared_atr_trail_close_test_reversal`

- FMZ source id: 473154 (lineage).
- Source: https://www.fmz.com/strategy/473154 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 16:39:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C214). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trailing line as a close test |
| 2 | PASS | EMA crossings with filters and an ATR trailing line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND472951. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50] x `atr_mult` [1.5, 3.0]: **8 trials**; the RSI levels fixed.

## Ambiguities resolved

- Shared, never-reset trail line (as written); exits are close tests. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
