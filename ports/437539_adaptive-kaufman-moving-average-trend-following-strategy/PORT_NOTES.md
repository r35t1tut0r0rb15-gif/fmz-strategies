# #437539 Adaptive Kaufman Moving Average Trend Following Strategy -> `fmz_437539_kama_prev_close_state`

- FMZ source id: 437539 (lineage).
- Source: https://www.fmz.com/strategy/437539 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-03 16:01:20). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C101). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close against an adaptive average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 10]: **2 trials**; the fast / slow ends fixed; reverse off.

## Ambiguities resolved

- KAMA from 0 as written; previous close against the current KAMA. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
