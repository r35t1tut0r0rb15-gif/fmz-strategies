# #458174 Dynamic Trend Following Trading Strategy Based on Gann Angles -> `fmz_458174_confirmed_swing_level_cross_reversal`

- FMZ source id: 458174 (lineage).
- Source: https://www.fmz.com/strategy/458174 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 15:53:39). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C202). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Swing-level crossings; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7]: **2 trials**; the angles have no effect (the term is 0); the per-bar bracket pending.

## Ambiguities resolved

- Gann lines equal the last swing levels (angle term 0, as written); per-bar bracket pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`trailing_stop_pending`
