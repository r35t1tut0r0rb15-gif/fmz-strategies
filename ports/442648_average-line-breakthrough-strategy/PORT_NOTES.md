# #442648 Average Line Breakthrough Strategy -> `fmz_442648_sd_band_reentry_reversal_pending_stops`

- FMZ source id: 442648 (lineage).
- Source: https://www.fmz.com/strategy/442648 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-23 14:46:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C160). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the event-set stops described (pending) |
| 2 | PASS | Band re-entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 20] x `mult` [2.0, 1.5]: **4 trials**; the stop percentage fixed (pending).

## Ambiguities resolved

- Event-set stops pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
