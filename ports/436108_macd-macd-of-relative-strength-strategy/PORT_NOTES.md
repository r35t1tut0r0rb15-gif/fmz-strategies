# #436108 相对强度MACD策略MACD-of-Relative-Strength-Strategy -> `fmz_436108_macd_of_relative_strength_long_stop`

- FMZ source id: 436108 (lineage).
- Source: https://www.fmz.com/strategy/436108 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-21 12:01:01). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C85). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | REVIEW | Relative-strength series and a percent stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed-ratio money management and cash order inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rs_length` [300, 150] x `sl_max` [0.08, 0.05]: **4 trials**; MACD 14 / 26 / 10 fixed.

## Ambiguities resolved

- Stop 8 % of the fill; re-entry while the histogram is positive. Mark coarse_bar_stop. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop`
