# #435965 Simple Moving Average Crossover Strategy -> `fmz_435965_sma_8_20_cross`

- FMZ source id: 435965 (lineage).
- Source: https://www.fmz.com/strategy/435965 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-20 14:36:08). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C84). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 5] x `slow` [20, 30]: **4 trials**.

## Ambiguities resolved

- Explicit closes equal the reversal. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
