# #473268 Dynamic Dual Moving Average Crossover Quantitative Trading Strategy -> `fmz_473268_ema9_21_cross_reversal_low_high_bracket_pending`

- FMZ source id: 473268 (lineage).
- Source: https://www.fmz.com/strategy/473268 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 17:15:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C215). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**; the per-bar bracket pending.

## Ambiguities resolved

- Per-bar bracket pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
