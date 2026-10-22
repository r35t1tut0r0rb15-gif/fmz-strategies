# #439268 基于T3指标的趋势追踪交易策略Trend-Following-Trading-Strategy-Based-on-T3-Indicator -> `fmz_439268_hpotter_t3_close_side`

- FMZ source id: 439268 (lineage).
- Source: https://www.fmz.com/strategy/439268 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-18 16:21:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C119). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close / T3 side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [5, 10] x `b` [0.7, 0.5]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
