# #485283 RSI反转斐波那契布林带量化策略-RSI-Reversal-Fibonacci-Bollinger-Bands-Quantitative-Strategy -> `fmz_485283_rsi_extreme_cross_pct_bracket`

- FMZ source id: 485283 (lineage).
- Source: https://www.fmz.com/strategy/485283 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-20 11:42:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry (re-issue marked). |
| 2 | PASS | An oscillator and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [1.0, 2.0] x `tp_pct` [2.0, 4.0]: **4 trials**; defaults 1 / 2 (the source's); RSI 14 (30 / 70) fixed.

## Trailing stop (mark `trailing_stop_pending`)

As written, every bar in a position re-issues `strategy.exit(limit = close x (1 +- 2 %), stop = close x (1 -+ 1 %))`
from the CURRENT close (a moving bracket). The port fixes it at entry (fractions of the fill).

## Ambiguities resolved

- The Fibonacci VWMA bands are plots only (no volume in the orders, check 8). REVERSAL INTENDED. Stop module:
  `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`
