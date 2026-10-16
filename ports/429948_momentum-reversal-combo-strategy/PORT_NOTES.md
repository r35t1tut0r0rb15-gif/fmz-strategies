# #429948 Momentum Reversal Combo Strategy -> `fmz_429948_combo_123_cmoabs`

- FMZ source id: 429948 (lineage).
- Source: https://www.fmz.com/strategy/429948 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-23 15:11:20). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG429948, ND429948. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_cmo` [9, 14] x `top_band` [70, 50]: **4 trials**; low band 20 and the 123 settings fixed.

## Ambiguities resolved

- Disagreement closes all. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
