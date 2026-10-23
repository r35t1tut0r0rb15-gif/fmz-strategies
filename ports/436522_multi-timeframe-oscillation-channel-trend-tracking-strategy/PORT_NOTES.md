# #436522 Multi Timeframe Oscillation Channel Trend Tracking Strategy -> `fmz_436522_dual_supertrend_agreement_daily_reversal`

- FMZ source id: 436522 (lineage).
- Source: https://www.fmz.com/strategy/436522 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-25 14:27:06). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Two-SuperTrend agreement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = 1 unit, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult1` [3.0, 2.0] x `mult2` [2.0, 1.5]: **4 trials**; periods 10 / 14.

## Ambiguities resolved

- Both SuperTrends on the chart (HTF input empty). Volume not used (VWAP filter off). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
