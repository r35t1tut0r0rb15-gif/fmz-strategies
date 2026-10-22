# #488004 多指标动态趋势跟踪交易系统EMA交叉MACD动量过滤ATR风险管理策略-Multi-Indicator-Dynamic-Trend-Following-Trading-System-EMA-Crossover-MACD-Momentum-Filter-ATR-Risk-Management-Strategy -> `fmz_488004_ema6_2_cross_macd18_19_24_atr7_bracket_reversal`

- FMZ source id: 488004 (lineage).
- Source: https://www.fmz.com/strategy/488004 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-24 13:08:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C264). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | EMA crossings with a MACD filter and an ATR bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atrMultiplier` [7.0, 3.0] x `shortEmaLength` [6, 10]: **4 trials**; EMA 2, ATR 13, MACD 18 / 19 / 24.

## Ambiguities resolved

- Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "2D" (two broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
