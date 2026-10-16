# #429576 EMA Oscillation Reversal System Strategy -> `fmz_429576_bb_width_expansion_chandelier`

- FMZ source id: 429576 (lineage).
- Source: https://www.fmz.com/strategy/429576 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-18 12:23:13). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exits. |
| 2 | PASS | Band-width changes and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`thresh` [9.0, 5.0] x `f` [4.0, 3.0]: **4 trials**; chandelier 22, EMA 50 / 20, BB 40 x 2 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_squeeze"`.

## Marks

`none`
