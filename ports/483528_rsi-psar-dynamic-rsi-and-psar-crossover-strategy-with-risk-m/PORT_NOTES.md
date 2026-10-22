# #483528 动态RSI与PSAR交叉策略结合风险管理系统-Dynamic-RSI-and-PSAR-Crossover-Strategy-with-Risk-Management-System -> `fmz_483528_sar_cross_rsi14_extreme_3_5pct_bracket_long`

- FMZ source id: 483528 (lineage).
- Source: https://www.fmz.com/strategy/483528 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-24 10:27:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C259). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | SAR crossings with RSI extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_percent` [5.0, 3.0] x `sl_percent` [3.0, 2.0]: **4 trials**; SAR 0.02 / 0.02 / 0.2, RSI 14 / 70 / 30.

## Ambiguities resolved

- A repeat signal's re-sent bracket is pending. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`trailing_stop_pending`
