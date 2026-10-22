# #483510 Multi Temporal Trend Identification Adaptive Position Management Strategy -> `fmz_483510_close_supertrend3_10_cross_dema100_side_reversal`

- FMZ source id: 483510 (lineage).
- Source: https://www.fmz.com/strategy/483510 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 16:49:07). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C259). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend line crossings with a DEMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `dema_length` [100, 50]: **4 trials**; ATR 10.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
