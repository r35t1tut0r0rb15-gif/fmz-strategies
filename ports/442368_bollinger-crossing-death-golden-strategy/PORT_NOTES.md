# #442368 Bollinger Crossing Death Golden Strategy -> `fmz_442368_bb50_breakout_reversal`

- FMZ source id: 442368 (lineage).
- Source: https://www.fmz.com/strategy/442368 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-21 14:19:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C154). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 20] x `mult` [2.5, 2.0]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
