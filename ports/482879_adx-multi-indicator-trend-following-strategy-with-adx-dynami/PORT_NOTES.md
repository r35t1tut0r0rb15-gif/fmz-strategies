# #482879 多指标综合趋势跟踪策略结合ADX动态交易系统-Multi-Indicator-Trend-Following-Strategy-with-ADX-Dynamic-Trading-System -> `fmz_482879_rsi_exit_extreme_ema_adx_atr_rr`

- FMZ source id: 482879 (lineage).
- Source: https://www.fmz.com/strategy/482879 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 16:20:04). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Moving averages, RSI, ADX and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [1.5, 2.5] x `rr` [2.0, 3.0]: **4 trials**; defaults 1.5 / 2 (the source's); EMA 20 / 50, RSI 14, ATR 14
and ADX 14 > 20 fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar. The port keeps the entry's bracket.

## Ambiguities resolved

- The ADX is the source's own (no up / down comparison), as written.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1min" ("GBP/USD" is a label).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`trailing_stop_pending`
