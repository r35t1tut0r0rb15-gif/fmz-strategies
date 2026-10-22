# #441002 Moving Average Crossover Strategy -> `fmz_441002_ema9_18_cross_reversal`

- FMZ source id: 441002 (lineage).
- Source: https://www.fmz.com/strategy/441002 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-04 16:00:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C144). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The initial capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 18] x `slow` [18, 36]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
