# #439878 Bandpass Filter Reversed Strategy -> `fmz_439878_hpotter_bandpass_reversed_state`

- FMZ source id: 439878 (lineage).
- Source: https://www.fmz.com/strategy/439878 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-24 15:28:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C126). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bandpass filter sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `delta` [0.5, 0.25]: **4 trials**; trigger 0 fixed.

## Ambiguities resolved

- Reversed sign as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "cycle_filter"`.

## Marks

`none`
