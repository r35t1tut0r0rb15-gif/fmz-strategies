# #482437 Adaptive Trend Following Strategy Based on Moving Average Crossover -> `fmz_482437_sma74_70_cross_point_bracket_flat_only`

- FMZ source id: 482437 (lineage).
- Source: https://www.fmz.com/strategy/482437 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 14:23:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C244). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; point bracket as fractions of the fill |
| 2 | PASS | SMA crossings with a point bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Trade size 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [74, 20] x `long_len` [70, 50]: **4 trials**; stop 353 / target 1059 points (fractions of 42000).

## Ambiguities resolved

- The points are price amounts (fractions of 42000). Entries only from flat (a loop follows the bracket). FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
