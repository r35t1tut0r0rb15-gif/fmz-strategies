# #488008 量子启发式概率趋势交易策略基于EMA和RSI的量化模型-Quantum-Inspired-Probability-Trend-Trading-Strategy-EMA-RSI-Based-Quantitative-Model -> `fmz_488008_logistic_ema_rsi_cycling_bracket`

- FMZ source id: 488008 (lineage).
- Source: https://www.fmz.com/strategy/488008 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-24 13:43:03). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | ADAPT | The 4.05-price-unit EMA gap -> 0.002 ATR; RSI and ATR. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trend_atr` [0.002, 0.25] x `tp_mult` [1.5, 2.0]: **4 trials**; defaults 0.002 / 1.5 (the source as written: the
logistic test `> 0.6` is an EMA 9 - EMA 55 gap above ln(1.5) / 0.1, about 4.05 price units, about 0.002 daily ATR on
BTC_USDT; judgement stated before any backtest); EMA 9 / 55, RSI 14, ATR 14, k 0.1 and the 50-bar decay cycle
fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar (its `strategy.exit`). The port keeps
the entry's bracket.

## Ambiguities resolved

- The RSI logistic test is RSI > about 52.0 (< about 48.0). `bar_index % 50` counts from the first bar of the data
  the module is given (as Pine counts from the chart's first bar). REVERSAL INTENDED. Stop module:
  `portfolio_kwargs` {} (D4). Daily bars are broker days; FREQ = "1D": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_filter"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
