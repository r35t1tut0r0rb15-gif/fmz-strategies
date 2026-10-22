# #489158 Advanced Dual Moving Average Crossover Trading System -> `fmz_489158_sma5_21_cross_long_3d`

- FMZ source id: 489158 (lineage).
- Source: https://www.fmz.com/strategy/489158 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-02 11:35:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C270). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent bracket pending |
| 2 | PASS | SMA crossings |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`shortLength` [5, 9] x `longLength` [21, 50]: **4 trials**.

## Ambiguities resolved

- The per-bar bracket is pending. Long only. FREQ = "3D" (three broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
