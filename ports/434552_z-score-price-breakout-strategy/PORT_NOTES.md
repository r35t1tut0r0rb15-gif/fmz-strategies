# #434552 Z Score Price Breakout Strategy -> `fmz_434552_zscore_side`

- FMZ source id: 434552 (lineage).
- Source: https://www.fmz.com/strategy/434552 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-07 15:17:43). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C68). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A z-score |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [20, 50] x `trigger` [0.0, 1.0]: **4 trials**; one trigger for both sides, as written.

## Ambiguities resolved

- One trigger for both sides, as written. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "zscore_reversion"`.

## Marks

`none`
