# #483114 基于双均线和动态订单块检测的智能资金流量化交易策略-Quantitative-Smart-Money-Flow-Trading-Strategy-with-Dual-EMA-and-Dynamic-Order-Block-Detection -> `fmz_483114_order_block_ema50_200_swing_bracket`

- FMZ source id: 483114 (lineage).
- Source: https://www.fmz.com/strategy/483114 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 14:10:33). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Moving averages and rolling swing extremes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [2.0, 3.0] x `swing_len` [5, 10]: **4 trials**; defaults 2 / 5 (the source's); EMA 50 / 200 fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar. The port keeps the entry's bracket.

## Ambiguities resolved

- The swing stop and the 2 R target become fractions of the signal close, picked by the signal's side, re-based on
  the fill; a signal whose stop is not beyond the close emits no entry (as #490798).
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h" ("XAU/EUR" is a label).

## FAMILY (proposed, user to confirm)

`FAMILY = "price_action"`.

## Marks

`trailing_stop_pending`
