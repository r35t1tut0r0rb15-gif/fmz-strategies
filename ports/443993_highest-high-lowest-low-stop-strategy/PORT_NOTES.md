# #443993 Highest High Lowest Low Stop Strategy -> `fmz_443993_three_close_run_channel_stop_pending`

- FMZ source id: 443993 (lineage).
- Source: https://www.fmz.com/strategy/443993 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-08 14:32:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C168). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the rolling channel stop described (pending) |
| 2 | PASS | Three-close runs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders while the stop is pending (the lookbacks feed only the stop): **1 trial**, the source as written.

## Ambiguities resolved

- The rolling channel stop pending (no exit). Entries only from flat. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`trailing_stop_pending`
