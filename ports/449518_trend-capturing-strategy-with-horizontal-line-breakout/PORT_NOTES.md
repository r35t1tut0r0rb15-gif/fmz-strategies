# #449518 Trend Capturing Strategy with Horizontal Line Breakout -> `fmz_449518_close_below_prior_low_toggle_long`

- FMZ source id: 449518 (lineage).
- Source: https://www.fmz.com/strategy/449518 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-26 15:22:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C179). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close-below-prior-low toggle |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written.

## Ambiguities resolved

- Line breakout never acts (empty array). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
