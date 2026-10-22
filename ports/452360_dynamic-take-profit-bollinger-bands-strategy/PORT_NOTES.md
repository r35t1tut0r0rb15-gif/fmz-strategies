# #452360 Dynamic Take Profit Bollinger Bands Strategy -> `fmz_452360_bollinger14_prev_bar_reentry_1pct_target_reversal`

- FMZ source id: 452360 (lineage).
- Source: https://www.fmz.com/strategy/452360 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-24 17:54:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C188). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the target as a fixed fraction; re-issued targets pending (mark) |
| 2 | PASS | Band re-entries with a fixed target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 20] x `mult` [2.0, 2.5] x `tp_pct` [0.01, 0.02]: **8 trials**.

## Ambiguities resolved

- Re-issued targets pending; opening level kept. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
