# #482590 多时框随机震荡指标策略与趋势确认交易系统-Multi-Timeframe-Stochastic-Oscillator-Strategy-with-Trend-Confirmation-Trading-System -> `fmz_482590_stoch_extreme_cross_swing_filter_pct_bracket`

- FMZ source id: 482590 (lineage).
- Source: https://www.fmz.com/strategy/482590 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-19 10:53:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | A stochastic, prior extremes and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [3.7, 2.0] x `tp_pct` [1.8, 3.6]: **4 trials**; defaults 3.7 / 1.8 (the source's); stochastic 15 / 4 / 5
(85 / 15) and the 5-bar swing filter fixed.

## Ambiguities resolved

- The 30- and 60-minute stochastics are requested but feed no order.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

none
