# #483032 自适应趋势跟踪与区间交易的双重策略系统-Adaptive-Dual-Strategy-System-for-Trend-Following-and-Range-Trading -> `fmz_483032_adx_switch_trend_range_atr_bracket`

- FMZ source id: 483032 (lineage).
- Source: https://www.fmz.com/strategy/483032 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:17:45). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Moving averages, ADX, Bollinger bands, RSI, MACD and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_level` [25.0, 20.0] x `tp_mult` [3.0, 2.0]: **4 trials**; defaults 25 / 3 (the source's); the 1.5 ATR stop and
all indicator lengths fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal under the same entry id while held re-places the stop and target from the new bar. The port keeps
the entry's bracket.

## Ambiguities resolved

- One position: a same-side entry under the other id is ignored, and its exit does nothing.
- A long and a short on one bar: the later short wins. ADX as `ta.dmi`; `ta.stdev` population.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "regime_switch"`.

## Marks

`trailing_stop_pending`
