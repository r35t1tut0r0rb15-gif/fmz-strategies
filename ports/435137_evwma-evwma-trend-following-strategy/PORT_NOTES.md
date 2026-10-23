# #435137 基于EVWMA指标的趋势跟踪策略EVWMA-Trend-Following-Strategy -> `fmz_435137_evwma_10_20_cross_daily_reversal`

- FMZ source id: 435137 (lineage).
- Source: https://www.fmz.com/strategy/435137 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-12 16:00:37). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume-weighted average crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_len` [10, 5] x `slow_len` [20, 40]: **4 trials**.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
