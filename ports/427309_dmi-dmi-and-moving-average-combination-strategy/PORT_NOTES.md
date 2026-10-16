# #427309 DMI and Moving Average Combination Strategy -> `fmz_427309_combo_123_dmi_ma`

- FMZ source id: 427309 (lineage).
- Source: https://www.fmz.com/strategy/427309 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-19 21:51:14). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator and cross states. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_ma` [30, 60] x `length_dmi` [14, 7]: **8 trials**; defaults 14 / 30 / 14 (the source's); K 1, D 3, level 50 fixed.

## Ambiguities resolved

- The DMI-MA state needs the DI cross and the MA cross on the same bar, strict comparisons as written.
- fFilter is never used; fixnan is causal. Disagreement closes (close_all). REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
