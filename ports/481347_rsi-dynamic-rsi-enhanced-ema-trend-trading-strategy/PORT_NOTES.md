# #481347 动态RSI增强型指数均线趋势交易策略-Dynamic-RSI-Enhanced-EMA-Trend-Trading-Strategy -> `fmz_481347_ema9_21_cross_rsi50_point_bracket_reversal`

- FMZ source id: 481347 (lineage).
- Source: https://www.fmz.com/strategy/481347 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-10 14:29:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C241). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; point bracket as fractions of the fill |
| 2 | PASS | EMA crossings with an RSI filter and a point bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Lot 1, capital 15000, risk 1000 / target 5000 stored; the bracket reduces to fixed points. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_frac` [7.14286e-04, 0.01] x `tp_frac` [3.57143e-03, 0.05]: **4 trials**; EMA 9 / 21, RSI 14.

## Ambiguities resolved

- The points are price amounts (fractions of 42000). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
