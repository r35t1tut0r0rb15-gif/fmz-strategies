# #436261 基于双均线和FRAMA指标的多空交叉交易策略FRAMA-and-Moving-Average-Crossover-Trading-Strategy-Based-on-Dual-Moving-Average -> `fmz_436261_frama_filtered_sma_cross_long`

- FMZ source id: 436261 (lineage).
- Source: https://www.fmz.com/strategy/436261 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-22 16:08:23). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C88). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Fractal adaptive average and an average cross |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG436261. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [16, 20] x `sc` [198, 100]: **4 trials**; SMA 13 / 26 and fast 1 fixed.

## Ambiguities resolved

- FRAMA from zero; previous raw dimension on a zero range. Long only. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
