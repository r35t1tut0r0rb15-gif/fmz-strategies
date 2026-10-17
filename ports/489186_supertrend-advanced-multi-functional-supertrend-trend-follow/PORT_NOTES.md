# #489186 高级多功能SuperTrend趋势跟踪策略与自动止盈止损系统-Advanced-Multi-functional-SuperTrend-Trend-Following-Strategy-with-Automated-Take-Profit-and-Stop-Loss-System -> `fmz_489186_supertrend_flip_always_in_3d`

- FMZ source id: 489186 (lineage).
- Source: https://www.fmz.com/strategy/489186 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-02 15:30:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_period` [10, 20] x `mult` [3.0, 2.0]: **4 trials**; defaults 10 / 3 (the source's).

## Ambiguities resolved

- The TP / SL / entry-offset block only draws labels (no orders): not ported. Always in after the first flip.
- Three-day bars from broker days in fixed blocks from 1970-01-01 (decision owed), as #426509. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
