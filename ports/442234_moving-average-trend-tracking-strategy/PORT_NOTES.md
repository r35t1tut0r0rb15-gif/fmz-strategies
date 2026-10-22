# #442234 Moving Average Trend Tracking Strategy -> `fmz_442234_plus_di_cross_pct_trail_long`

- FMZ source id: 442234 (lineage).
- Source: https://www.fmz.com/strategy/442234 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-20 14:36:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C153). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail is a house trail (approximation stated) |
| 2 | PASS | DI crossings and a percent trail on highs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`di_len` [6, 14] x `trail_pct` [0.03, 0.05]: **4 trials**.

## Ambiguities resolved

- Percent trail on highs as a house trail (stated). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`coarse_bar_stop, trailing_stop`
