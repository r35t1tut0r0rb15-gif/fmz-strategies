# #442817 双移动平均-HullMA交叉趋势策略Dual-Moving-Average-HullMA-Crossover-Trend-Strategy -> `fmz_442817_close_direction_hull_turn_reversal`

- FMZ source id: 442817 (lineage).
- Source: https://www.fmz.com/strategy/442817 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-26 11:21:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C161). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close direction with a Hull turn |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG442817. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`keh` [7, 14]: **2 trials**.

## Ambiguities resolved

- The profit-gated closes repeat the reversals (not ported). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
