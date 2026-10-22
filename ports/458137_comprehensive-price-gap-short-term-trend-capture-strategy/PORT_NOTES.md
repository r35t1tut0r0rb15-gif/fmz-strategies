# #458137 Comprehensive Price Gap Short Term Trend Capture Strategy -> `fmz_458137_gap_down_short_point_target_flags`

- FMZ source id: 458137 (lineage).
- Source: https://www.fmz.com/strategy/458137 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 11:08:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C202). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the point target as a fraction of the fill |
| 2 | PASS | Opening-gap shorts with a point target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`gap_frac` [0.00357, 0.01] x `target_frac` [0.00119, 0.005]: **4 trials**; the 11:00 cut-off fixed.

## Ambiguities resolved

- Daily close[1] from the last completed broker day; points as fractions of 42000; later-armed targets pending; marketable target one bar late. Short only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`trailing_stop_pending`
