# #453277 Starlight Moving Average Crossover Strategy -> `fmz_453277_sma20_50_cross_long`

- FMZ source id: 453277 (lineage).
- Source: https://www.fmz.com/strategy/453277 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 16:45:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C193). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [20, 10] x `long_len` [50, 100]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
