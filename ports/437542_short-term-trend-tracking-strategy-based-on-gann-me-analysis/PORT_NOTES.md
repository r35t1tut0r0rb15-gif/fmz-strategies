# #437542 Short term Trend Tracking Strategy Based on Gann Me Analysis Indicator -> `fmz_437542_ema_ribbon_difference_cross`

- FMZ source id: 437542 (lineage).
- Source: https://www.fmz.com/strategy/437542 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-03 16:10:08). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C102). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Sign of an EMA ribbon difference |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`scale` [1.0, 2.0] (every EMA length times the scale): **2 trials**.

## Ambiguities resolved

- Long when the slow ribbon rises above the fast one, as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
