# #483130 动态均线交叉结合RSI动量和ATR波动率的多层级确认交易策略-Dynamic-EMA-Crossover-with-RSI-Momentum-and-ATR-Volatility-Multi-Level-Confirmation-Trading-Strategy -> `fmz_483130_ema9_21_cross_rsi_atr_bracket`

- FMZ source id: 483130 (lineage).
- Source: https://www.fmz.com/strategy/483130 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 14:53:32). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Moving averages, RSI and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based qty quoted, not ported; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [1.5, 2.0] x `tp_mult` [3.0, 4.0]: **4 trials**; defaults 1.5 / 3 (the source's); EMA 9 / 21, RSI 14
(70 / 30) and ATR 14 fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar. The port keeps the entry's bracket.

## Ambiguities resolved

- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h" ("BTC" is a label).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
