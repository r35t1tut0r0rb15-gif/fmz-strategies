# #488523 多重均线回归MACD趋势确认策略-Multiple-EMA-Reversion-MACD-Trend-Confirmation-Strategy -> `fmz_488523_ema_ribbon_macd_atr_bracket`

- FMZ source id: 488523 (lineage).
- Source: https://www.fmz.com/strategy/488523 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-28 15:40:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | EMAs, MACD and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [5.0, 3.0] x `rr` [1.5, 2.0]: **4 trials**; defaults 5 / 1.5 (the source's); EMAs 20 / 250 / 2 / 100 / 300,
MACD 12 / 26 / 9 and ATR 14 fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held is ignored as an entry, but its `strategy.exit` re-places the stop and target from the
new signal bar's close and ATR. The port keeps the entry's bracket (fixed at the signal bar, re-based on the fill).

## Ambiguities resolved

- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h" (no coarse-bar mark).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_filter"`.

## Marks

`trailing_stop_pending`
