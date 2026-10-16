# #430598 Breakout Trading Strategy with Scalability -> `fmz_430598_swing_range_breaker`

- FMZ source id: 430598 (lineage).
- Source: https://www.fmz.com/strategy/430598 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-30 17:25:17). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving target fixed at the fill (rule 2). |
| 2 | PASS | Swing levels and a percentage target. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out 10 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`swing_lookback` [20, 10] x `target_pct` [5.0, 2.5]: **4 trials**.

## Ambiguities resolved

- Pending (not emitted as written): the target re-issued from each close; fixed at the fill here.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks

`trailing_stop_pending`
