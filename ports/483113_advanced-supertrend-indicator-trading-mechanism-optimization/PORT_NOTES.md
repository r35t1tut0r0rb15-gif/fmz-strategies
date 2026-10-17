# #483113 高级超趋势指标交易机制优化策略-Advanced-Supertrend-Indicator-Trading-Mechanism-Optimization-Strategy -> `fmz_483113_supertrend_change_cross_1d`

- FMZ source id: 483113 (lineage).
- Source: https://www.fmz.com/strategy/483113 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 15:05:49). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Supertrend (ATR bands). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [0.25, 1.0] x `length` [6, 10]: **4 trials**; defaults 0.25 / 6 (the source's).

## Ambiguities resolved

- `ta.supertrend` as TradingView documents it. `prevSupertrend` is the previous bar's line, so the `valuewhen`
  condition is "the line changed on this bar", and `valuewhen(..., 1)` is the direction on the second most recent such
  bar (0 by `nz` before one exists).
- REVERSAL INTENDED (always in once started); no exits or stops. Broker days stamped with their first minute (as
  #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
