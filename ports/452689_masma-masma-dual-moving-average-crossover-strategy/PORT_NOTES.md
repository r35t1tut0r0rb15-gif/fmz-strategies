# #452689 MASMA双均线交叉策略-MASMA-Dual-Moving-Average-Crossover-Strategy -> `fmz_452689_sma20_50_cross_reversal`

- FMZ source id: 452689 (lineage).
- Source: https://www.fmz.com/strategy/452689 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-28 10:53:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C188). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Spot pair in the header only (the source sends shorts as written). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [20, 10] x `long_len` [50, 100]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
