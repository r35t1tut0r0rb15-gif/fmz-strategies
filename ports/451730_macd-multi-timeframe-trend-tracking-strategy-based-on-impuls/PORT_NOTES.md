# #451730 基于脉冲MACD和双均线交叉的多时间尺度趋势追踪策略-Multi-timeframe-Trend-Tracking-Strategy-Based-on-Impulse-MACD-and-Dual-Moving-Average-Crossover -> `fmz_451730_impulse_macd_signal_cross_long`

- FMZ source id: 451730 (lineage).
- Source: https://www.fmz.com/strategy/451730 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-17 15:33:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C187). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Impulse MACD signal crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_ma` [34, 20] x `length_signal` [9, 5]: **4 trials**.

## Ambiguities resolved

- The broken SMA block ignored. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
