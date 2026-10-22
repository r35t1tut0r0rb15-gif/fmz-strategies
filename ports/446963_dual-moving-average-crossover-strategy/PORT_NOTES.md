# #446963 Dual Moving Average Crossover Strategy -> `fmz_446963_sma9_21_cross_long_moving_bracket_pending`

- FMZ source id: 446963 (lineage).
- Source: https://www.fmz.com/strategy/446963 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-03 15:12:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C177). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket not ported (mark) |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the percent bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**.

## Ambiguities resolved

- Bracket re-sent from each close: pending. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
