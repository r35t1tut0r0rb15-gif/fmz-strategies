# #442823 The Dual Reversal Strategy -> `fmz_442823_reversal123_three_bar_pattern_combo`

- FMZ source id: 442823 (lineage).
- Source: https://www.fmz.com/strategy/442823 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-26 12:07:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C161). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close pattern, stochastic and 3-bar pattern states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `level` [50, 40]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
