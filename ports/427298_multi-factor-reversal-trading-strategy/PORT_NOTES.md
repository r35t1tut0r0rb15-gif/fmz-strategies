# #427298 Multi-factor Reversal Trading Strategy -> `fmz_427298_combo_123_pfe`

- FMZ source id: 427298 (lineage).
- Source: https://www.fmz.com/strategy/427298 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-19 21:13:04). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | PFE mixes price differences with bar counts; price differences measured in ATR(14) units. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_pfe` [9, 20] x `band` [50, 30]: **8 trials**; defaults 14 / 9 / 50 (the source's); K 1, D 3, level 50, EMA 5 fixed; bands symmetric.

## Ambiguities resolved

- As written PFE depends on the price scale (`sqrt(diff^2 + 100)`): one ATR counts as one bar in the port. The constant 100 (10^2) is kept as written for a 9-bar length.
- The combo is flat when the two states disagree (close_all). REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
