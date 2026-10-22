# #443104 双EMA金叉死叉趋势追踪策略Dual-EMA-Crossover-Trend-Tracking-Strategy -> `fmz_443104_last_4h_ema10_21_cross_daily_reversal`

- FMZ source id: 443104 (lineage).
- Source: https://www.fmz.com/strategy/443104 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-29 11:45:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C166). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the 4-hour values end with the day |
| 2 | PASS | Lower-time-frame EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len3` [10, 5] x `len2` [21, 50]: **4 trials**.

## Ambiguities resolved

- 4-hour values as the day's last 4-hour bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`
