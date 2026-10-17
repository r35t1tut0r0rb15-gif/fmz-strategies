# #482841 动态自适应多时间周期趋势跟踪与震荡反转复合策略-Dynamic-Adaptive-Multi-Timeframe-Trend-Following-and-Range-Reversal-Hybrid-Strategy -> `fmz_482841_ichimoku_regime_macd_rsi_stoch_atr_stop_2d`

- FMZ source id: 482841 (lineage).
- Source: https://www.fmz.com/strategy/482841 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 14:48:41). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-placed stop fixed at entry (marked). |
| 2 | PASS | Rolling mid-points, MACD, RSI, stochastic and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the stop via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [2.0, 3.0] x `base_len` [26, 20]: **4 trials**; defaults 2 / 26 (the source's); conversion 9, span B 52,
MACD 12 / 26 / 9, RSI 14, stochastic 14 / 3 / 3 and ATR 14 fixed.

## Trailing stop (mark `trailing_stop_pending`)

Each signal bar re-issues `strategy.exit` with the stop at that bar's low - 2 ATR (high + 2 ATR), so a later signal
of the same entry while held moves the stop. The port fixes it at the entry's signal bar (re-based on the fill).

## Ambiguities resolved

- The leading spans are not displaced (as written). The "Stochastic RSI" is the stochastic of the close.
- Trend and range entries of one side share the position (pyramiding 1). REVERSAL INTENDED. Stop module:
  `portfolio_kwargs` {} (D4). Two-day bars: blocks of broker-day dates from 1970-01-01 (decision owed, #426509).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`, `trailing_stop_pending`
