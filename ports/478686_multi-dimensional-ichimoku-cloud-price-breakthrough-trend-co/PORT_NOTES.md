# #478686 Multi Dimensional Ichimoku Cloud Price Breakthrough Trend Confirmation Trading Strategy -> `fmz_478686_sma_ichimoku_base_spanA_cross_long`

- FMZ source id: 478686 (lineage).
- Source: https://www.fmz.com/strategy/478686 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 14:21:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C238). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku-style line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conversion` [9, 20] x `base` [26, 60]: **4 trials**.

## Ambiguities resolved

- SMA-of-hl2 lines, as written. Long only. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
