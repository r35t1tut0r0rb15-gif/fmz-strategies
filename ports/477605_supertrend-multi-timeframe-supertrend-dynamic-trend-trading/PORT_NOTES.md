# #477605 多时间周期Supertrend趋势交易策略的动态组合算法-Multi-Timeframe-Supertrend-Dynamic-Trend-Trading-Algorithm -> `fmz_477605_mtf_supertrend_15_5_2min_daily_long`

- FMZ source id: 477605 (lineage).
- Source: https://www.fmz.com/strategy/477605 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 16:38:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C236). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; lower-time-frame lines from each day's last block |
| 2 | PASS | Multi-time-frame SuperTrend alignment |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and capital 50000 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `atr_period` [10, 20]: **4 trials**; the 15 / 5 / 2-minute series fixed.

## Ambiguities resolved

- Lower-time-frame lines at each day's last block. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
