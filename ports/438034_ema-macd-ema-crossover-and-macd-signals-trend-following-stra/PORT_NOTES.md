# #438034 基于EMA均线和MACD指标的趋势跟踪策略EMA-Crossover-and-MACD-Signals-Trend-Following-Strategy -> `fmz_438034_ema9_21_cross_close_side`

- FMZ source id: 438034 (lineage).
- Source: https://www.fmz.com/strategy/438034 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-08 14:31:56). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C108). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**; the per-bar bracket pending.

## Ambiguities resolved

- Per-bar bracket from the latest close kept pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
