# #488382 多因子顶部旋转反转策略与风险收益优化系统-Multi-Factor-Spinning-Top-Reversal-Strategy-with-Risk-Reward-Optimization -> `fmz_488382_spinning_top_colour_change_bracket`

- FMZ source id: 488382 (lineage).
- Source: https://www.fmz.com/strategy/488382 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-27 09:54:23). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | ADAPT | The 4-price-unit buffer -> 0.1 ATR; candle proportions. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`buffer_atr` [0.1, 0.5] x `rr` [1.5, 2.0]: **4 trials**; defaults 0.1 / 1.5 (the source as written: 4 price units on
3-hour ETH_USDT, ATR about 40, are about 0.1 ATR; judgement stated before any backtest); body 30 %, wick balance 20 %
and ATR 14 fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar (its `strategy.exit`). The port keeps
the entry's bracket (fixed at the signal bar, picked by the signal's side, re-based on the fill).

## Ambiguities resolved

- The stop sits beyond the signal bar's extreme plus the buffer; the target is `rr` x the stop distance from the
  close. REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "3h": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
