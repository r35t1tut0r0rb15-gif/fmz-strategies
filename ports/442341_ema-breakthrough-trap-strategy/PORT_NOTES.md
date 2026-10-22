# #442341 EMA Breakthrough Trap Strategy -> `fmz_442341_bull_bear_trap_range_target_reversal`

- FMZ source id: 442341 (lineage).
- Source: https://www.fmz.com/strategy/442341 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-21 11:29:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C154). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed at entry from signal-bar data |
| 2 | PASS | Trap tests and a range target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [5, 10] x `ema_length` [21, 50]: **4 trials**; ATR multiplier 1 and the 80 % target fixed.

## Ambiguities resolved

- Target from the signal close, re-based on the fill. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`coarse_bar_stop`
