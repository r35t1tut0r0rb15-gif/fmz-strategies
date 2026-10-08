# #395962 Highest high/lowest low stop -> `fmz_395962_three_closes_hl_stop`

- Source: https://www.fmz.com/strategy/395962 (PineScript v4, author Zer3192, FMZ last
  modified 2023-01-07 21:10:04). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hi_len` [10, 20, 40] x `lo_len` [10, 20, 40] = **9 trials**.

## Ambiguities resolved

- The stop is re-set every bar (moving): `trailing_stop_pending`; the port fixes it at the signal bar's level (sl_stop fraction, shifted one bar).
- Entries from flat only; simulate() mirrors the engine stop; `upon_opposite_entry="ignore"`.
- No bar size in the source: `FREQ = "bar_size_pending"` (rule 1).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks (2026-10-07)

`bar_size_pending, trailing_stop_pending`
