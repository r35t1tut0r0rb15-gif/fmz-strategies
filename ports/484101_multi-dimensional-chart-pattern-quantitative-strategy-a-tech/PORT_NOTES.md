# #484101 多维图表模式量化策略融合头肩顶底与双顶底形态的技术分析交易系统-Multi-Dimensional-Chart-Pattern-Quantitative-Strategy-A-Technical-Analysis-Trading-System-Integrating-Head-and-Shoulders-and-Double-Top-Bottom-Formations -> `fmz_484101_five_bar_swing_pattern_bracket`

- FMZ source id: 484101 (lineage).
- Source: https://www.fmz.com/strategy/484101 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-28 10:19:51). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Bar patterns and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [1.5, 2.5] x `atr_len` [14, 7]: **4 trials**; defaults 1.5 / 14 (the source's); target 2 x the stop.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar (its `strategy.exit`). The port keeps
the entry's bracket.

## Ambiguities resolved

- The patterns as written (the head-and-shoulders test is identical to the double-top test and unused). REVERSAL
  INTENDED. Stop module: `portfolio_kwargs` {} (D4). Two-day bars are blocks of broker-day dates from 1970-01-01
  (decision owed, as #426509); FREQ = "2D": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "chart_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
