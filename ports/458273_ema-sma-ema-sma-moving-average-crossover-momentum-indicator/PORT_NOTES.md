# #458273 EMA-SMA-均线交叉-动量指标-EMA-SMA-Moving-Average-Crossover-Momentum-Indicator -> `fmz_458273_ema9_cross_sma30_exit_sma30_or_50_long`

- FMZ source id: 458273 (lineage).
- Source: https://www.fmz.com/strategy/458273 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 14:41:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C205). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA / SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [9, 5] x `sma1` [30, 20] x `sma2` [50, 100]: **8 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
