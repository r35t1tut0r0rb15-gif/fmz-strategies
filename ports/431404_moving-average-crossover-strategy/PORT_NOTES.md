# #431404 Moving Average Crossover Strategy -> `fmz_431404_sma_trima_cross_long`

- FMZ source id: 431404 (lineage).
- Source: https://www.fmz.com/strategy/431404 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-07 15:48:41). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C45). Not run.

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

`fast` [5, 10] x `n` [10, 20]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
