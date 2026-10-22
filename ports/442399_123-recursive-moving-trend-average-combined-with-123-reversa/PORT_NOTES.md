# #442399 递归移动趋势均线结合123形态反转的组合策略Recursive-Moving-Trend-Average-Combined-with-123-Reversal-Pattern-Strategy -> `fmz_442399_reversal123_rmta_combo`

- FMZ source id: 442399 (lineage).
- Source: https://www.fmz.com/strategy/442399 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-21 16:02:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C155). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close pattern, stochastic and RMTA states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_rmta` [21, 10]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
