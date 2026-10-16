# #430662 基于EMA和MAMA指标的交易策略EMA-and-MAMA-Indicators-Based-Trading-Strategy -> `fmz_430662_emama_cross`

- FMZ source id: 430662 (lineage).
- Source: https://www.fmz.com/strategy/430662 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-31 14:20:56). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Adaptive moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_limit` [0.5, 0.3] x `slow_limit` [0.05, 0.02]: **4 trials**; source hl2 fixed.

## Ambiguities resolved

- Radians and nz() kept as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
