# #482816 动态自适应多指标交叉策略结合SRSI和MACD的智能风控系统-Dynamic-Adaptive-Multi-Indicator-Crossing-Strategy-with-SRSI-MACD-Smart-Risk-Control-System -> `fmz_482816_stoch_rsi_macd_turn_atr_bracket_long`

- FMZ source id: 482816 (lineage).
- Source: https://www.fmz.com/strategy/482816 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:44:09). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at entry (marked). |
| 2 | PASS | A stochastic RSI, MACD and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`risk` [2.5, 1.5] x `rsi_len` [16, 14]: **4 trials**; defaults 2.5 / 16 (the source's); stochastic 16 / 3 / 3,
MACD 12 / 26 / 9 and ATR 14 fixed.

## Trailing stop (mark `trailing_stop_pending`)

The exit is re-issued every bar from `strategy.position_avg_price` with the current ATR, so stop and target move
with volatility. The port fixes them at the signal bar's ATR (re-based on the fill). Decision owed as #489289
(bracket from the average price applied from the fill).

## Ambiguities resolved

- Flat-only entries: `simulate()` mirrors the house bracket from the fill (as #430254). Long only.
- Stop module: `portfolio_kwargs` {} (D4). Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`coarse_bar_stop`, `trailing_stop_pending`
