# #489009 Multi Dynamic Indicator Combination Strategy -> `fmz_489009_wick_supertrend22_3_flip_bb_band_exit_reversal`

- FMZ source id: 489009 (lineage).
- Source: https://www.fmz.com/strategy/489009 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-01 10:12:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C268). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend flips with Bollinger band exits |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Capital 100000, 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`st_mult` [3.0, 2.0] x `st_length` [22, 10]: **4 trials**; BB 20 / 2.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2D" (two broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
