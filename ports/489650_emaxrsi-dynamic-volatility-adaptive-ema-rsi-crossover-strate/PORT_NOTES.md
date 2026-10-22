# #489650 动态波动率自适应EMAxRSI交叉策略-Dynamic-Volatility-Adaptive-EMA-RSI-Crossover-Strategy -> `fmz_489650_ema20_50_cross_rsi_atr_bracket_reversal_2d`

- FMZ source id: 489650 (lineage).
- Source: https://www.fmz.com/strategy/489650 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-07 13:25:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C272). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | EMA crossings with RSI / trend filters and an ATR bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Risk-sized lot stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stopLossMultiplier` [1.0, 2.0] x `takeProfitMultiplier` [2.0, 4.0]: **4 trials**; EMA 20 / 50, RSI 14, ATR 14.

## Ambiguities resolved

- Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "2D" (two broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
