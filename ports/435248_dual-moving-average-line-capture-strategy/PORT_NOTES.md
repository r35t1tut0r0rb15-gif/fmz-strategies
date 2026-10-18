# #435248 Dual Moving Average Line Capture Strategy -> `fmz_435248_stormer_narrow_bb_bracket`

- FMZ source id: 435248 (lineage).
- Source: https://www.fmz.com/strategy/435248 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-13 15:28:50). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C76). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar |
| 2 | PASS | Band breakouts, an average filter and swing exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [0.38, 1.0] x `target` [1.6, 3.0]: **4 trials**; BB 20, EMA 80 and the 7-bar stops fixed.

## Ambiguities resolved

- Signal-bar bracket re-based on the fill. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
