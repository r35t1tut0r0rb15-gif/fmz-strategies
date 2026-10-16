# #430767 Bollinger带震荡型突破策略Bollinger-Bands-Oscillation-Breakthrough-Strategy -> `fmz_430767_bb_basis_aroon_scalp_long`

- FMZ source id: 430767 (lineage).
- Source: https://www.fmz.com/strategy/430767 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-01 16:45:54). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bollinger bands and an Aroon level. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out 30 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_ar` [288, 144] x `confirmation` [90, 80]: **4 trials**; BB 20 / 2 and the Aroon stop 70 fixed.

## Ambiguities resolved

- Entry and close on one bar: flat if already long, long if flat. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
