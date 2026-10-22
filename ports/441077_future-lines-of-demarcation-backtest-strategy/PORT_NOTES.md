# #441077 Future Lines of Demarcation Backtest Strategy -> `fmz_441077_fld_hl2_displaced_40_reversal`

- FMZ source id: 441077 (lineage).
- Source: https://www.fmz.com/strategy/441077 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-05 14:00:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C146). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Displaced median price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [40, 20]: **2 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
