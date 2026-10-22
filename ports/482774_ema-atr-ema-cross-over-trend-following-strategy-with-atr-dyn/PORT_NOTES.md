# #482774 EMA交叉趋势追踪与ATR动态止损优化策略-EMA-Cross-Over-Trend-Following-Strategy-with-ATR-Dynamic-Stop-Loss-Optimization -> `fmz_482774_ema5_200_cross_resent_atr2_stop_tp5_long`

- FMZ source id: 482774 (lineage).
- Source: https://www.fmz.com/strategy/482774 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:51:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C248). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent target from the fill; re-sent ATR stop followed in the loop (pending) |
| 2 | PASS | EMA 5 / 200 crossings with an ATR stop and a percent target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [2.0, 3.0] x `take_profit_perc` [5.0, 10.0]: **4 trials**; EMA 5 / 200, ATR 14.

## Ambiguities resolved

- The re-sent stop is pending; the loop closes on the touching bar's close, one bar late.
- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
