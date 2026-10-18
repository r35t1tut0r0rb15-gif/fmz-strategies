# #436092 DEMA策略MACD指标组合DEMA-MACD-Combination-Strategy -> `fmz_436092_dema_position_macd_filter`

- FMZ source id: 436092 (lineage).
- Source: https://www.fmz.com/strategy/436092 (PineScript v1, author ChaoZhang, FMZ last
  modified 2023-12-21 10:49:45). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C85). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | DEMA position and a MACD filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`dema_length` [21, 34] x `macd_control` [False, True]: **4 trials**.

## Ambiguities resolved

- States every bar; histogram filter in the grid. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
