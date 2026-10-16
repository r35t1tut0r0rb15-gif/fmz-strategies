# #427613 Dual MACD StochRSI Trading Strategy -> `fmz_427613_macdouble_stochrsi`

- FMZ source id: 427613 (lineage).
- Source: https://www.fmz.com/strategy/427613 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-22 16:55:55). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry. |
| 2 | ADAPT | 9000-tick loss -> `sl_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; stop quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_rsi` [11, 14] x `buy_trig` [90, 80] x `sl_atr` [30, 10]: **8 trials**; defaults 11 / 90 / 30; the MACD lengths and the sell trigger 20 fixed. 900 USD on 1-minute BTC is about 30 ATR (judgement before any backtest).

## Ambiguities resolved

- The custom-resolution switches default to the chart's period; the custom resolutions are not ported.
- `(kRes and dRes < 90)` as written: K non-zero and not na, and D < 90.
- The exit has no `from_entry`, so once issued it guards every position; the port guards every position from the first (stated approximation).
- The year window is dropped. Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
