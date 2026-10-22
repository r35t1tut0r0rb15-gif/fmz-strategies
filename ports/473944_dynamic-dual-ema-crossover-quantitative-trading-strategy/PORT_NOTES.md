# #473944 Dynamic Dual EMA Crossover Quantitative Trading Strategy -> `fmz_473944_ema13_21_cross_reversal`

- FMZ source id: 473944 (lineage).
- Source: https://www.fmz.com/strategy/473944 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-04 15:37:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C220). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [13, 8] x `long_len` [21, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
