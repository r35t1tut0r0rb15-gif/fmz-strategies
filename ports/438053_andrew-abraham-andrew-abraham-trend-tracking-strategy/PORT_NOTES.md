# #438053 Andrew-Abraham趋势追踪策略Andrew-Abraham-Trend-Tracking-Strategy -> `fmz_438053_abraham_trend_trader`

- FMZ source id: 438053 (lineage).
- Source: https://www.fmz.com/strategy/438053 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-08 16:21:11). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C109). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel line from extremes and average true range |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND434966. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 14] x `mult` [3.0, 2.0]: **4 trials**; reverse off.

## Ambiguities resolved

- Level-state entries. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
