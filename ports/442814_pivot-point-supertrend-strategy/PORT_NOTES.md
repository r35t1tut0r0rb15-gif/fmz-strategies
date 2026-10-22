# #442814 Pivot Point SuperTrend Strategy -> `fmz_442814_pivot_point_supertrend_flip_reversal`

- FMZ source id: 442814 (lineage).
- Source: https://www.fmz.com/strategy/442814 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-26 10:57:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C161). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; pivots used once confirmed |
| 2 | PASS | Pivot SuperTrend and classic SuperTrend flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The cash size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `prd` [2, 5]: **4 trials** (one factor for both lines, as their defaults agree); the ATR periods and the SMA fixed.

## Ambiguities resolved

- Pivots once confirmed; later short wins a tie. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
