# #435953 Dual Moving Average Intelligent Tracking Strategy -> `fmz_435953_smart_ma_state_long`

- FMZ source id: 435953 (lineage).
- Source: https://www.fmz.com/strategy/435953 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-20 13:50:47). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C83). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`base_ma_length` [50, 100] x `mode` ["Composite", "Crossover", "Direction"]: **6 trials**; fast 10 and slow 30 fixed.

## Ambiguities resolved

- Modes in the grid; MA type unused. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
