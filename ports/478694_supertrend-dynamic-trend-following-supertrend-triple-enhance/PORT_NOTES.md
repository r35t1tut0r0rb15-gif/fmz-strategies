# #478694 动态趋势追踪与均线辅助的SuperTrend三重优化策略-Dynamic-Trend-Following-SuperTrend-Triple-Enhancement-Strategy -> `fmz_478694_supertrend16_flip_ema49_point_stop_close_trail_flat_only`

- FMZ source id: 478694 (lineage).
- Source: https://www.fmz.com/strategy/478694 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 14:37:39). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C238). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend flips on the EMA side with point stops and a close trail |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.02, 2.0] x `ma_period` [49, 100]: **4 trials**; ATR 16; stop 50 / trail 70 points (fractions of 42000).

## Ambiguities resolved

- The point amounts are price amounts (fractions of 42000). Entries only from flat. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
