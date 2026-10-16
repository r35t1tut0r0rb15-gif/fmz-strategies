# #427883 Double Reversal RSI Momentum Strategy -> `fmz_427883_combo_123_reversal_rsi_roc`

- FMZ source id: 427883 (lineage).
- Source: https://www.fmz.com/strategy/427883 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-26 15:42:48). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C13). Not run.
- Near-duplicate group: **ND426888** (31 members, best partner #440094, Jaccard 0.669); ported anyway (rule 7).

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

`length` [14, 21] x `rsi_length` [20, 14]: **4 trials**; defaults 14 / 20 (the source's); K 1, D 3, level 50, ROC 20, zones 30 / 70 fixed.

## Ambiguities resolved

- "Trade reverse" fixed off. Disagreement closes the position. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
