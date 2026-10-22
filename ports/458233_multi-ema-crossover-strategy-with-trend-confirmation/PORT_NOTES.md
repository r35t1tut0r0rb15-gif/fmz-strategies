# #458233 Multi EMA Crossover Strategy with Trend Confirmation -> `fmz_458233_ema8_21_cross_above_ema200_long`

- FMZ source id: 458233 (lineage).
- Source: https://www.fmz.com/strategy/458233 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 11:08:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C204). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings above a long EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 5] x `slow` [21, 34] x `trend` [200, 100]: **8 trials**; the EMA 50 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
