# #488284 动态双EMA趋势捕捉与ATR风控量化策略-Dynamic-Dual-EMA-Trend-Capture-with-ATR-Risk-Management-Quantitative-Strategy -> `fmz_488284_ema9_15_cross_atr_bracket`

- FMZ source id: 488284 (lineage).
- Source: https://www.fmz.com/strategy/488284 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 15:44:55). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L10). Not run.

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

`sl_mult` [1.0, 2.0] x `rr` [1.5, 2.0]: **4 trials**; defaults 1 / 1.5 (the source's); EMA 9 / 15 and ATR 14 fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held (a second cross after an unconfirmed opposite cross) re-places the stop and target
from the new bar (its `strategy.exit`). The port keeps the entry's bracket (fixed at the signal bar, re-based on the
fill).

## Ambiguities resolved

- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). Daily bars are broker days; FREQ = "1D":
  `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
