# #436595 Dual Channel Donchian Breakout Strategy -> `fmz_436595_donchian_separate_channels`

- FMZ source id: 436595 (lineage).
- Source: https://www.fmz.com/strategy/436595 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-26 10:18:51). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C92). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length1` [20, 30] x `length2` [20, 10]: **4 trials**.

## Ambiguities resolved

- Offset input unused. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
