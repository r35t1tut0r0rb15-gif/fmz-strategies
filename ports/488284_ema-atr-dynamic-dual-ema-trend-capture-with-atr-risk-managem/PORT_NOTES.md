# #488284 动态双EMA趋势捕捉与ATR风控量化策略-Dynamic-Dual-EMA-Trend-Capture-with-ATR-Risk-Management-Quantitative-Strategy -> `fmz_488284_ema9_15_cross_atr_stop_15r_reversal`

- FMZ source id: 488284 (lineage).
- Source: https://www.fmz.com/strategy/488284 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 15:44:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C266). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | EMA crossings with an ATR bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slMultiplier` [1.0, 2.0] x `riskRewardRatio` [1.5, 3.0]: **4 trials**; EMA 9 / 15, ATR 14.

## Ambiguities resolved

- Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
