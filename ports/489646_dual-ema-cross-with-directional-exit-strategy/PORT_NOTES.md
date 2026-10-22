# #489646 Dual EMA Cross with Directional Exit Strategy -> `fmz_489646_ema5_21_cross_reversal`

- FMZ source id: 489646 (lineage).
- Source: https://www.fmz.com/strategy/489646 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-07 12:00:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C272). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Capital 10000, 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 9] x `slow` [21, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
