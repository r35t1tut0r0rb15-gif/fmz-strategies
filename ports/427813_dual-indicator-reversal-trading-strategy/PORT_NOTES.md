# #427813 Dual Indicator Reversal Trading Strategy -> `fmz_427813_combo_123_reversal_cci`

- FMZ source id: 427813 (lineage).
- Source: https://www.fmz.com/strategy/427813 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-25 17:46:24). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C12). Not run.
- Near-duplicate group: **ND426888** (31 members, best partner #432231, Jaccard 0.663); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21] x `fast_ma` [10, 5]: **4 trials**; defaults 14 / 10 (the source's); K 1, D 3, level 50, CCI 10 and slow MA 20 fixed.

## Ambiguities resolved

- "Trade reverse" fixed off. Disagreement closes the position. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
