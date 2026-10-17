# #488004 多指标动态趋势跟踪交易系统EMA交叉MACD动量过滤ATR风险管理策略-Multi-Indicator-Dynamic-Trend-Following-Trading-System-EMA-Crossover-MACD-Momentum-Filter-ATR-Risk-Management-Strategy -> `fmz_488004_ema6_2_cross_macd_7atr_bracket`

- FMZ source id: 488004 (lineage).
- Source: https://www.fmz.com/strategy/488004 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-24 13:08:42). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | EMAs, MACD and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [7.0, 3.0] x `short_len` [6, 9]: **4 trials**; defaults 7 / 6 (the source's); EMA 2, MACD 18 / 19 / 24 and
ATR 13 fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar (its `strategy.exit`). The port keeps
the entry's bracket.

## Ambiguities resolved

- The EMA lengths as written (the "short" EMA 6 is the slower one). REVERSAL INTENDED. Stop module:
  `portfolio_kwargs` {} (D4). Two-day bars are blocks of broker-day dates from 1970-01-01 (decision owed, as
  #426509); FREQ = "2D": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
