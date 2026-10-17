# #483793 增强型十字星烛台趋势反转量化交易策略-Enhanced-Doji-Candlestick-Trend-Reversal-Quantitative-Trading-Strategy -> `fmz_483793_doji_confirm_closeout_bracket`

- FMZ source id: 483793 (lineage).
- Source: https://www.fmz.com/strategy/483793 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:33:27). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | ADAPT | 5 ticks -> about 0.00025 ATR; candle proportions. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.00025, 1.0] x `rr` [2.0, 3.0]: **4 trials**; defaults 0.00025 / 2 (the source as written: on 2-day
ETH_USDT, tick 0.01 and ATR about 200, 5 ticks are about 0.00025 ATR; judgement stated before any backtest); the 30 %
doji test and ATR 14 fixed.

## Ambiguities resolved

- Every doji closes the position held coming into the bar (#430850: never the entry made on it); both
  confirmations on one doji: the short (written last) wins. The SMA trend is unused. A same-side doji signal while
  held is also a close-out bar, so no re-placement. REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
  Two-day bars are blocks of broker-day dates from 1970-01-01 (decision owed, as #426509); FREQ = "2D":
  `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick_pattern"`.

## Marks

`coarse_bar_stop`
