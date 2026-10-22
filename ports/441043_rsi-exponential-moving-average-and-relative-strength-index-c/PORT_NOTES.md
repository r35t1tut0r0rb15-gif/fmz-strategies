# #441043 均线与RSI指标结合的趋势跟踪策略Exponential-Moving-Average-and-Relative-Strength-Index-Combination-Trend-Following-Strategy -> `fmz_441043_ema5_13_cross_ema50_side_rsi_exit`

- FMZ source id: 441043 (lineage).
- Source: https://www.fmz.com/strategy/441043 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-05 09:57:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C144). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings and RSI exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The default quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trend_len` [50, 100] x `rsi_length` [14, 9]: **4 trials**; EMA 5 / 13 and RSI levels fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
