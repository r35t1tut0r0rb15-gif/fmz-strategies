# #438771 Quantitative Trading Strategy Based on Supertrend Indicator and Equity Curve Trading -> `fmz_438771_atr_trend_change_equity_display`

- FMZ source id: 438771 (lineage).
- Source: https://www.fmz.com/strategy/438771 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-15 11:41:53). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C112). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR trend line changes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`periods` [10, 14] x `multiplier` [3.0, 4.0]: **4 trials**; source hl2 fixed.

## Ambiguities resolved

- Equity-curve filter display only. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
