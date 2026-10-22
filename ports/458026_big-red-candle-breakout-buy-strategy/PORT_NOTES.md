# #458026 Big Red Candle Breakout Buy Strategy -> `fmz_458026_big_red_candle_low_undercut_long`

- FMZ source id: 458026 (lineage).
- Source: https://www.fmz.com/strategy/458026 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 13:31:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C198). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the per-bar bracket pending (mark) |
| 2 | PASS | Big-red-candle undercut reversals |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity rule and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`range_frac` [0.000476, 0.01]: **2 trials**.

## Ambiguities resolved

- The per-bar bracket pending; no exit. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`trailing_stop_pending`
