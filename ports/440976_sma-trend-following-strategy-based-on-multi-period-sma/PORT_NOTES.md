# #440976 基于多周期SMA指标的趋势跟踪策略Trend-Following-Strategy-Based-on-Multi-Period-SMA -> `fmz_440976_sma_racer_zero_lag_exits`

- FMZ source id: 440976 (lineage).
- Source: https://www.fmz.com/strategy/440976 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-04 14:50:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C142). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA stack slopes and zero-lag EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`dir_span` [4, 8] x `zl_slow` [21, 34]: **4 trials**; the SMA lengths and zero-lag fast 9 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
