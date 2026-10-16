# #429485 Surf Rider Strategy -> `fmz_429485_combo_123_eco`

- FMZ source id: 429485 (lineage).
- Source: https://www.fmz.com/strategy/429485 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-17 15:30:18). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels and a dimensionless ratio. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`r` [32, 16] x `s` [12, 6]: **4 trials**; 123 settings fixed.

## Ambiguities resolved

- Disagreement closes all. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
