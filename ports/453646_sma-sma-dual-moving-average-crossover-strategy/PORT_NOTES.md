# #453646 SMA双均线交叉策略-SMA-Dual-Moving-Average-Crossover-Strategy -> `fmz_453646_sma50_200_golden_cross_long`

- FMZ source id: 453646 (lineage).
- Source: https://www.fmz.com/strategy/453646 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-07 14:49:52). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C192). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Golden / death crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [50, 20] x `long_len` [200, 100]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
