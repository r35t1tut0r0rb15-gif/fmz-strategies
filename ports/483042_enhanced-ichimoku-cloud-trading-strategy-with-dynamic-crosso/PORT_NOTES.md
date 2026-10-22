# #483042 Enhanced Ichimoku Cloud Trading Strategy with Dynamic Crossover Signals -> `fmz_483042_tenkan9_kijun26_cross_long`

- FMZ source id: 483042 (lineage).
- Source: https://www.fmz.com/strategy/483042 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 10:41:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C255). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Tenkan / Kijun crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conversion_periods` [9, 7] x `base_periods` [26, 22]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
