# #475595 Multi Trendline Breakout Momentum Quantitative Strategy -> `fmz_475595_pivot_trendline_atr_slope_break_reversal`

- FMZ source id: 475595 (lineage).
- Source: https://www.fmz.com/strategy/475595 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-20 14:26:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C228). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Pivot trendline breaks |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 20] x `mult` [1.0, 0.5]: **4 trials**; Atr slope method.

## Ambiguities resolved

- Atr slope method (default). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
