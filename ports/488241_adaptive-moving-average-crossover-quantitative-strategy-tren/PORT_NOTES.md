# #488241 Adaptive Moving Average Crossover Quantitative Strategy Trend Following and Trading Signal Optimization -> `fmz_488241_sma9_21_cross_long`

- FMZ source id: 488241 (lineage).
- Source: https://www.fmz.com/strategy/488241 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 11:09:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C265). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fastLength` [9, 5] x `slowLength` [21, 50]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
