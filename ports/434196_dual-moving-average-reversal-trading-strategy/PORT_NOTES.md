# #434196 Dual Moving Average Reversal Trading Strategy -> `fmz_434196_hull_direction`

- FMZ source id: 434196 (lineage).
- Source: https://www.fmz.com/strategy/434196 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-04 16:39:13). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C65). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | The slope of an average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [32, 64] x `reaction` [2, 4]: **4 trials**; MA type HullMA fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
