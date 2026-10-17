# #483122 多层移动平均线交叉精确时序趋势跟踪策略-Multi-Layer-Moving-Average-Cross-Precise-Timing-Trend-Following-Strategy -> `fmz_483122_sma50_touch_sma_stack_sma20_exit`

- FMZ source id: 483122 (lineage).
- Source: https://www.fmz.com/strategy/483122 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 14:32:49). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`use_tick_cross` [True, False] x `fast` [20, 10]: **4 trials**; defaults True / 20 (the source's); SMA 50 / 100 / 200
fixed.

## Ambiguities resolved

- The closes come after the entries: they act on the position held at the bar's start and never undo an entry on that
  bar (as #430850); target-position state machine, exits emitted only on going flat.
- A long and a short entry on one bar: the later (short) wins, as in Pine.
- REVERSAL INTENDED. No stops. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
