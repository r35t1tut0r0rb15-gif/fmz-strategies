# #482454 Adaptive-Trend-Detection-Strategy-with-Dual-Envelope-EMA-System-基于双包络EMA系统的自适应趋势检测策略 -> `fmz_482454_andean_bull_bear_always_in`

- FMZ source id: 482454 (lineage).
- Source: https://www.fmz.com/strategy/482454 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 15:06:49). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Exponential envelopes of prices and squared prices. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 100]: **2 trials**; default 50 (the source's). The signal length feeds no order.

## Ambiguities resolved

- The envelopes start at the `var` value 0, as written; a negative variance (rounding) gives na, as Pine's sqrt.
- REVERSAL INTENDED (always in). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
