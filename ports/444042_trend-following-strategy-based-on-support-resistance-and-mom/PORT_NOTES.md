# #444042 Trend Following Strategy Based on Support Resistance and Momentum Indicators Across Multiple Timeframes -> `fmz_444042_pivot_supertrend_72x4_hlc3_flip_reversal`

- FMZ source id: 444042 (lineage).
- Source: https://www.fmz.com/strategy/444042 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-08 17:41:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C170). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; pivots used once confirmed |
| 2 | PASS | Pivot SuperTrend and classic SuperTrend flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [4.0, 2.0] x `prd` [1, 3]: **4 trials**; the classic SuperTrend's 3 x 4, the pivot ATR period and the SMA fixed.

## Ambiguities resolved

- Pivots once confirmed; later short wins a tie. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
