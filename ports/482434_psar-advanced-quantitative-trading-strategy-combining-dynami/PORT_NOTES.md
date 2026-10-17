# #482434 动态布林带结合PSAR指标的高级量化交易策略-Advanced-Quantitative-Trading-Strategy-Combining-Dynamic-Bollinger-Bands-with-PSAR-Indicator -> `fmz_482434_bb_break_strong_body_window_bar_stop_rr3`

- FMZ source id: 482434 (lineage).
- Source: https://www.fmz.com/strategy/482434 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 14:11:00). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-placed bracket fixed at entry (marked). |
| 2 | PASS | Bollinger bands, candle proportions and the signal bar's range. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_mult` [2.0, 1.5] x `rr` [3, 2]: **4 trials**; defaults 2 / 3 (the source's); BB 20 and the 33 % body fixed.

## Trailing stop (mark `trailing_stop_pending`)

Each signal bar re-issues `strategy.exit` with its own low / high and 3 R target, so a later same-side signal while
held moves the bracket. The port keeps the entry's levels.

## Ambiguities resolved

- Clock rule (check 9 / C6): `timestamp("GMT-5", ...)` is a fixed UTC-5 (no DST): 07:30-16:00 there is
  12:30-21:00 UTC on the bar's opening time; two-hour bars at 14, 16, 18 and 20 UTC qualify.
- The PSAR only feeds a drawing. A zero-length stop emits no entry.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`coarse_bar_stop`, `trailing_stop_pending`
