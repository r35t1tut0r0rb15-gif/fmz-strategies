# #433425 A Double Moving Average Crossover Trading Strategy -> `fmz_433425_sma_10_50_cross`

- FMZ source id: 433425 (lineage).
- Source: https://www.fmz.com/strategy/433425 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-27 15:32:57). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C60). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [10, 20] x `len2` [50, 100]: **4 trials**; MA types SMA fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
