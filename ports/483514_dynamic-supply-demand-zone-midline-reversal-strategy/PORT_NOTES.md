# #483514 Dynamic Supply Demand Zone Midline Reversal Strategy -> `fmz_483514_range50_midpoint_rejection_sma20_zone_bracket_reversal`

- FMZ source id: 483514 (lineage).
- Source: https://www.fmz.com/strategy/483514 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-24 16:00:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C259). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; zone bracket as fractions of the fill |
| 2 | PASS | Midpoint rejections with range-edge brackets |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 100] x `midline_length` [20, 50]: **4 trials**.

## Ambiguities resolved

- A repeat signal's close_all / re-entry and re-sent bracket are pending; the first trade is kept. MPL 2.0 source, ported and stated.
- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion_band"`.

## Marks

`trailing_stop_pending`
