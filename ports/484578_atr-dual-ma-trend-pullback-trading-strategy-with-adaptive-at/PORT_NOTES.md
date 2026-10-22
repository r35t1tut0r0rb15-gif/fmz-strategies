# #484578 双均线趋势回调自适应ATR止盈止损量化交易策略-Dual-MA-Trend-Pullback-Trading-Strategy-with-Adaptive-ATR-Based-Risk-Management -> `fmz_484578_ema10_50_pullback_reclaim_atr2_2r_bracket_reversal`

- FMZ source id: 484578 (lineage).
- Source: https://www.fmz.com/strategy/484578 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-03 09:49:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C261). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | EMA trend pullbacks with an ATR bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_ma_length` [10, 20] x `sl_multiplier` [2.0, 1.5]: **4 trials**; EMA 50, ATR 14, target 2R.

## Ambiguities resolved

- A repeat signal's re-sent bracket is pending. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
