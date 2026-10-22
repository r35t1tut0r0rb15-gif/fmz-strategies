# #482873 Multi Level Quantitative Trend Trading Strategy Based on Support Resistance Breakout and Retest -> `fmz_482873_pivot3_3_break_retest_0_5pct_reversal`

- FMZ source id: 482873 (lineage).
- Source: https://www.fmz.com/strategy/482873 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 16:00:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C252). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Pivot level break-and-retest |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pivot_bars` [3, 5] x `tolerance` [0.005, 0.01]: **4 trials**; left = right bars.

## Ambiguities resolved

- The header's 1d wins over the title's 4hr. Break and retest may share a bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
