# #489153 Hourly Open Close Price Differential Smart Comparison Quantitative Trading System -> `fmz_489153_open_over_prev_close_close_target3pct_long`

- FMZ source id: 489153 (lineage).
- Source: https://www.fmz.com/strategy/489153 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-02 11:15:52). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C269). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested percent target |
| 2 | PASS | Gap-up entries with a percent target |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`target_pct` [3.0, 1.5, 6.0]: **3 trials**.

## Ambiguities resolved

- A loop follows the position for the close-tested target. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "gap"`.

## Marks

`none`
