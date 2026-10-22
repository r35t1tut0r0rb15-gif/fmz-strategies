# #451076 Multi Timeframe Reversal Confirmation Trading Strategy -> `fmz_451076_extreme_bar_reversal_break_reversal`

- FMZ source id: 451076 (lineage).
- Source: https://www.fmz.com/strategy/451076 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-11 17:38:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C184). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Breaks of the extreme bar's opposite end |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [50, 20]: **2 trials**.

## Ambiguities resolved

- Oldest matching bar's level, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
