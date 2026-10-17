# #482500 多重指标交叉动态自适应趋势跟踪交易策略Multi-Indicator-Cross-Adaptive-Trend-Following-Trading-Strategy -> `fmz_482500_ema6_20_cross_lsma333_rsi50_pct_bracket`

- FMZ source id: 482500 (lineage).
- Source: https://www.fmz.com/strategy/482500 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 17:17:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | EMAs, a regression line, RSI and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lsma_len` [333, 200] x `tp_pct` [2, 4]: **4 trials**; defaults 333 / 2 (the source's); EMA 6 / 20, RSI 14 and the
1 % stop fixed.

## Ambiguities resolved

- LSMA is `ta.linreg(close, 333, 0)`, the regression line's end value. REVERSAL INTENDED. Stop module:
  `portfolio_kwargs` {} (D4). Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`
