# #438485 Exponential Moving Average Crossover Strategy -> `fmz_438485_ema20_50_cross_ema200_side`

- FMZ source id: 438485 (lineage).
- Source: https://www.fmz.com/strategy/438485 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-12 14:04:37). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C111). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings and EMA 200 side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The cash size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `mid` [50, 100]: **4 trials**; EMA 200 fixed.

## Ambiguities resolved

- Exits name unused ids: none placed. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
