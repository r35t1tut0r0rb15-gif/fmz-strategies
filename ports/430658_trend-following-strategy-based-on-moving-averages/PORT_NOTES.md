# #430658 trend following strategy based on moving averages -> `fmz_430658_sma10_50_cross_short_stop`

- FMZ source id: 430658 (lineage).
- Source: https://www.fmz.com/strategy/430658 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-31 14:00:47). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the shared-id exit read as written, the moving stop fixed at the fill. |
| 2 | PASS | Moving averages and a percentage stop. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 20] x `slow` [50, 100]: **4 trials**; stop 1 % fixed.

## Ambiguities resolved

- Pending (as written, not emitted for longs): longs have no stop (shared id); the short's moving stop is fixed at the fill.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
