# #483682 波动率过滤双均线交叉高夏普比策略-Volatility-Filtered-Dual-EMA-Crossover-High-Sharpe-Ratio-Strategy -> `fmz_483682_ema10_30_cross_atr_spike_bracket`

- FMZ source id: 483682 (lineage).
- Source: https://www.fmz.com/strategy/483682 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-25 11:23:13). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at entry (marked). |
| 2 | PASS | Moving averages and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based qty quoted, not ported; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [2.0, 1.5] x `tp_mult` [4.0, 3.0]: **4 trials**; defaults 2 / 4 (the source's); EMA 10 / 30, ATR 14 and the
20-bar ATR mean / stdev fixed.

## Trailing stop (mark `trailing_stop_pending`)

Both `strategy.exit` calls run on every bar, from the current close and ATR: the stop and target move with price. The
port fixes them at the signal bar (re-based on the fill).

## Ambiguities resolved

- `ta.stdev` is the population standard deviation. The risk-based qty and the slippage input are not ported.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
