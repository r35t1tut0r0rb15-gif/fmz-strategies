# #448774 基于MACD信号线交叉与ATR风险管理的优化趋势跟踪策略-Optimized-MACD-Trend-Following-Strategy-with-ATR-based-Risk-Management -> `fmz_448774_macd_cross_below_zero_green_atr_bracket_long`

- FMZ source id: 448774 (lineage).
- Source: https://www.fmz.com/strategy/448774 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-18 17:15:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C178). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed on the signal bar |
| 2 | PASS | MACD cross-ups below zero with an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [2.0, 1.0] x `tp_mult` [5.0, 3.0]: **4 trials**; the MACD lengths and ATR 5 fixed.

## Ambiguities resolved

- Bracket from the signal bar. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop`
