# #483063 基于EMA交叉与RSI过滤的自适应动态止盈止损策略-Adaptive-Dynamic-Stop-Loss-and-Take-Profit-Strategy-Based-on-EMA-Crossover-and-RSI-Filter -> `fmz_483063_ema9_21_cross_rsi_atr_bracket_pending`

- FMZ source id: 483063 (lineage).
- Source: https://www.fmz.com/strategy/483063 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:06:29). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Moving averages, RSI and ATR multiples. |
| 3 | PASS | No exchange named. |
| 4 | DONE | 100 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [2.5, 1.5] x `rr` [2.0, 3.0]: **4 trials**; defaults 2.5 / 2 (the source's); EMA 9 / 21, ATR 14 and RSI 14
(70 / 30) fixed.

## Bar size (mark `bar_size_pending`)

No backtest header and no bar size in the source: `FREQ = "bar_size_pending"`; `precompute` builds the bars with
`bar_sizes.build_bars(raw_1m_df, params["bar_size"])` (the driver supplies `bar_size`).

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar. The port keeps the entry's bracket.

## Ambiguities resolved

- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`bar_size_pending, trailing_stop_pending`
