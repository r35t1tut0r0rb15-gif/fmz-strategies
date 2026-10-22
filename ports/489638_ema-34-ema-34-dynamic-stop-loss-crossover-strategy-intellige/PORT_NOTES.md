# #489638 EMA-34-动态止损交叉策略趋势跟踪与风险管理的智能结合-EMA-34-Dynamic-Stop-Loss-Crossover-Strategy-Intelligent-Combination-of-Trend-Following-and-Risk-Management -> `fmz_489638_close_ema34_cross_prevlow_stop_10r_breakeven_long`

- FMZ source id: 489638 (lineage).
- Source: https://www.fmz.com/strategy/489638 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-07 11:39:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C272). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; level touches sent as closes |
| 2 | PASS | EMA crossings with a candle-low stop, R target and break-even move |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [34, 20] x `rr` [10.0, 3.0]: **4 trials**; break-even at 3 R.

## Ambiguities resolved

- Touches are sent as closes, in a loop. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
