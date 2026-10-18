# #436254 Moving Average Crossover Long Short Trading Strategy -> `fmz_436254_sma_20_50_cross_3min`

- FMZ source id: 436254 (lineage).
- Source: https://www.fmz.com/strategy/436254 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-22 15:13:50). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C88). Not run.

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

`fast` [20, 10] x `slow` [50, 100]: **4 trials**.

## Ambiguities resolved

- Explicit closes equal the reversal. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
