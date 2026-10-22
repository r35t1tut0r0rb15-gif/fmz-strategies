# #486564 Dual Moving Average Crossover Trading System A Quantitative Strategy Based on Short term and Medium term MA Breakthrough -> `fmz_486564_sma7_10_cross_long`

- FMZ source id: 486564 (lineage).
- Source: https://www.fmz.com/strategy/486564 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-14 09:27:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C263). Not run.

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

`fast` [7, 5] x `slow` [10, 20]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
