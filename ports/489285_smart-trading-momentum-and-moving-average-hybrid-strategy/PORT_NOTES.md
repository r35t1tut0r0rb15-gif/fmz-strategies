# #489285 Smart Trading Momentum and Moving Average Hybrid Strategy -> `fmz_489285_sma13_5_cross_reversal`

- FMZ source id: 489285 (lineage).
- Source: https://www.fmz.com/strategy/489285 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-03 10:42:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C270). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Risk-sized quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [13, 20] x `slow` [5, 10]: **4 trials**.

## Ambiguities resolved

- The brackets never act (unentered ids). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
