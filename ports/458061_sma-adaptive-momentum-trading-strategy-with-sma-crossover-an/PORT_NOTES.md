# #458061 SMA交叉结合超趋势的自适应动量交易策略Adaptive-Momentum-Trading-Strategy-with-SMA-Crossover-and-SuperTrend -> `fmz_458061_sma20_50_cross_supertrend_target_reversal`

- FMZ source id: 458061 (lineage).
- Source: https://www.fmz.com/strategy/458061 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 16:38:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C200). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the fill-price target as a fixed fraction |
| 2 | PASS | SMA crossings with a Supertrend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma1` [20, 10] x `sma2` [50, 100] x `tp_pct` [0.01, 0.03]: **8 trials**; the Supertrend fixed.

## Ambiguities resolved

- Target from the fill bar; no stop. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`coarse_bar_stop`
