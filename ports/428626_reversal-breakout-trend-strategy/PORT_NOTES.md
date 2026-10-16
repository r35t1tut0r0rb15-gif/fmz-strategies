# #428626 Reversal Breakout Trend Strategy -> `fmz_428626_combo_123_reversal_breakout_long`

- FMZ source id: 428626 (lineage).
- Source: https://www.fmz.com/strategy/428626 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-07 16:15:43). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C18). Not run.
- Near-duplicate group: **ND426888** (31 members, best partner #440369, Jaccard 0.715); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels and channel lengths. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21] x `look_bak` [4, 10]: **4 trials**; defaults 14 / 4 (the source's); K 1, D 3, level 50 fixed.

## Ambiguities resolved

- The breakout leg is 1 / 0, never -1: the short combination cannot occur (Long only); every non-signal bar closes the long, as written.
- "Trade reverse" fixed off. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
