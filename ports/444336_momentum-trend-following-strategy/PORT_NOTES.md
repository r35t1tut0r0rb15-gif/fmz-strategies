# #444336 Momentum Trend Following Strategy -> `fmz_444336_aroon_56_20_cross_long`

- FMZ source id: 444336 (lineage).
- Source: https://www.fmz.com/strategy/444336 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-11 10:54:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C170). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Aroon line crossings |
| 3 | PASS | Exchange pair in the header only; ETHERIUM in the title only. |
| 4 | DONE | The 100 % of equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len_upper` [56, 25] x `len_lower` [20, 25]: **4 trials**; the floor 5 fixed.

## Ambiguities resolved

- Shorts off by the direction input. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
