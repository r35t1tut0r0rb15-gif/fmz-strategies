# #457792 Bollinger Bands and RSI Crossover Trading Strategy -> `fmz_457792_bollinger_reentry_rsi_extreme_reversal`

- FMZ source id: 457792 (lineage).
- Source: https://www.fmz.com/strategy/457792 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-26 16:16:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C198). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band re-entries with RSI extremes |
| 3 | PASS | No exchange named. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 2.5] x `rsi_len` [14, 7]: **8 trials**; the levels fixed.

## Ambiguities resolved

- No bar size (bar_size_pending). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`bar_size_pending`
