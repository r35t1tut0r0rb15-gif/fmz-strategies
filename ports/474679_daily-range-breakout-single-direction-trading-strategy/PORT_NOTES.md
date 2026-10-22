# #474679 Daily Range Breakout Single Direction Trading Strategy -> `fmz_474679_prev_day_range_break_point_bracket_from_flat`

- FMZ source id: 474679 (lineage).
- Source: https://www.fmz.com/strategy/474679 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 15:23:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C222). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the point bracket as fractions of the signal close |
| 2 | PASS | Previous-day range breaks with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_frac` [0.00119, 0.0119] x `tp_frac` [0.00119, 0.0119]: **4 trials**.

## Ambiguities resolved

- Points as fractions of 42000. The daily flags feed nothing on daily bars. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`coarse_bar_stop`
