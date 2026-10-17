# #482848 波动率动量突破交易策略结合趋势和动量过滤-Volatility-Momentum-Breakout-Strategy-with-Trend-and-Momentum-Filters -> `fmz_482848_atr_breakout_ema_rsi_atr_rr`

- FMZ source id: 482848 (lineage).
- Source: https://www.fmz.com/strategy/482848 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 15:13:31). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at entry (marked). |
| 2 | PASS | Rolling extremes, an EMA, RSI and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 5 % of equity and the risk input quoted; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 1.0] x `rr` [2.0, 3.0]: **4 trials**; defaults 1.5 / 2 (the source's); ATR 14, lookback 20, EMA 50,
RSI 14 and the 1 ATR stop fixed.

## Trailing stop (mark `trailing_stop_pending`)

The exits run every bar from the fill with the current ATR, so stop and target move with volatility. The port fixes
them at the signal bar (re-based on the fill).

## Ambiguities resolved

- Every bar in the condition is an entry signal. REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
  FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`trailing_stop_pending`
