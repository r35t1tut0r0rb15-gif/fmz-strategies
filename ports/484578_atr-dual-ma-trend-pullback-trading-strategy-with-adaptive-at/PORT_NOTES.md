# #484578 双均线趋势回调自适应ATR止盈止损量化交易策略-Dual-MA-Trend-Pullback-Trading-Strategy-with-Adaptive-ATR-Based-Risk-Management -> `fmz_484578_ema_pullback_reclaim_bracket`

- FMZ source id: 484578 (lineage).
- Source: https://www.fmz.com/strategy/484578 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-03 09:49:20). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | EMAs and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [2.0, 1.5] x `fast` [10, 20]: **4 trials**; defaults 2 / 10 (the source's); EMA 50, ATR 14 and the 2 x
target fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar (its `strategy.exit`). The port keeps
the entry's bracket.

## Ambiguities resolved

- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "2h": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
