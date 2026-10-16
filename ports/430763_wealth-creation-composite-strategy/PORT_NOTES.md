# #430763 Wealth Creation Composite Strategy -> `fmz_430763_combo_123_accelerator`

- FMZ source id: 430763 (lineage).
- Source: https://www.fmz.com/strategy/430763 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-01 16:28:55). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels and slopes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430763. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_slow` [34, 55] x `length_fast` [5, 8]: **4 trials**; the 123 settings fixed.

## Ambiguities resolved

- Disagreement closes all. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
