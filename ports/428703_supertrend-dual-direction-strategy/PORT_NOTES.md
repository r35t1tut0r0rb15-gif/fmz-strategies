# #428703 SuperTrend Dual Direction Strategy -> `fmz_428703_supertrend_late_flip`

- FMZ source id: 428703 (lineage).
- Source: https://www.fmz.com/strategy/428703 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-08 15:02:45). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders (the intrabar settings are in a commented-out line). |
| 2 | PASS | An ATR multiple. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital / position / commission constants and the commented-out strategy() stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`periods` [10, 14] x `multiplier` [3.0, 2.0]: **4 trials**; source hl2 fixed.

## Ambiguities resolved

- One-bar-late entries as written. The commented-out strategy() settings are inert.
- REVERSAL INTENDED. FREQ = "3D" (blocks of 3 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
