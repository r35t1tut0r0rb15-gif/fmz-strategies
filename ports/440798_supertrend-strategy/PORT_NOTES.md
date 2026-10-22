# #440798 SuperTrend Strategy -> `fmz_440798_classic_supertrend_state`

- FMZ source id: 440798 (lineage).
- Source: https://www.fmz.com/strategy/440798 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-02 11:11:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C140). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Supertrend state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Cash size and capital are sizing. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`periods` [10, 20] x `multiplier` [3.0, 2.0]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
