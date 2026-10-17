# #434478 Multi Moving Average Crossover Trading Strategy -> `fmz_434478_three_smma_state`

- FMZ source id: 434478 (lineage).
- Source: https://www.fmz.com/strategy/434478 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-06 17:10:00). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C67). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed averages |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [7, 5] x `long_len` [21, 42]: **4 trials**; the middle SMMA 13 fixed.

## Ambiguities resolved

- SMMA seeded by the SMA; date window dropped. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
