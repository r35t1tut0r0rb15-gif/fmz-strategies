# #438940 优化自适应智能多因子Hull渔人策略Hull-Fisher-Adaptive-Intelligent-Multi-factor-Strategy -> `fmz_438940_hull_fisher_cci_filters`

- FMZ source id: 438940 (lineage).
- Source: https://www.fmz.com/strategy/438940 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-16 15:10:06). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C114). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Fisher transform of a Hull MA, CCI and slopes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [14, 28] x `length` [9, 18]: **4 trials**; lines 5 / -5 and the filters fixed.

## Ambiguities resolved

- Only the CCI + HMA conditions apply; closes before entries. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
