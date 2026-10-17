# #488133 季度EMA动态回撤交易系统-Quarterly-EMA-Pullback-Trading-System -> `fmz_488133_ema_reclaim_rsi40_long`

- FMZ source id: 488133 (lineage).
- Source: https://www.fmz.com/strategy/488133 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-25 13:15:22). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at the signal bar (moves marked). |
| 2 | PASS | EMAs, an oscillator and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the stop via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_max` [40, 50] x `sl_pct` [15.0, 5.0]: **4 trials**; defaults 40 / 15 (the source's); EMA 10 / 21, RSI 14 and the
8 % jump exit fixed.

## Trailing stop (mark `trailing_stop_pending`)

`entryPrice` is reassigned on every signal, also while held, and `strategy.exit(stop = entryPrice x 0.85)` is
re-issued every bar, so a later signal moves the stop. The port keeps the entry's stop (15 % of the fill).

## Ambiguities resolved

- The close acts on the position at the bar's start (#430850); `simulate()` mirrors the stop from the fill bar
  (#430254). Long only: opposite entries cannot occur. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`trailing_stop_pending`
