# #442651 Trend Following Strategy Based on Moving Average Combination -> `fmz_442651_super_guppy_ribbon_stack_long`

- FMZ source id: 442651 (lineage).
- Source: https://www.fmz.com/strategy/442651 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-23 14:54:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C160). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stacked EMA ribbons |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`step` [3, 2] x `slow_start` [24, 30]: **4 trials** (fast EMAs step x 1..7; slow EMAs slow_start + step x 0..14).

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
