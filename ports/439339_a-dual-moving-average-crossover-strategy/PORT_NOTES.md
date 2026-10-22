# #439339 A Dual Moving Average Crossover Strategy -> `fmz_439339_sma10_30_cross_bracket_pending`

- FMZ source id: 439339 (lineage).
- Source: https://www.fmz.com/strategy/439339 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-19 14:13:07). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C119). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the per-bar bracket pending |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_length` [10, 20] x `slow_length` [30, 50]: **4 trials**.

## Ambiguities resolved

- Per-bar bracket from the current close pending (entries only). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
