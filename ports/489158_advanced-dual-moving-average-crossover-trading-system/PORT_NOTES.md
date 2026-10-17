# #489158 高级双均线策略交叉交易系统-Advanced-Dual-Moving-Average-Crossover-Trading-System -> `fmz_489158_sma_5_21_cross_bracket_long_3d`

- FMZ source id: 489158 (lineage).
- Source: https://www.fmz.com/strategy/489158 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-02 11:35:32). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at entry (mark). |
| 2 | PASS | SMAs and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [1.0, 3.0] x `tp_pct` [2.0, 6.0]: **4 trials**; defaults 1 / 2 (the source's); SMA 5 / 21 fixed.

## Moving bracket (rule 2, mark `trailing_stop_pending`)

`strategy.exit(stop = close x 0.99, limit = close x 1.02)` runs every bar: the levels follow the close. Fixed at
1 % / 2 % of the fill here.

## Ambiguities resolved

- Long only; the cross down is a close-based exit. Three-day bars from broker days in fixed blocks from 1970-01-01
  (decision owed), as #426509: `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
