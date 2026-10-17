# #433008 Bi Directional Trend Tracking Moving Average Crossover Strategy -> `fmz_433008_occ_alma_cross`

- FMZ source id: 433008 (lineage).
- Source: https://www.fmz.com/strategy/433008 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-23 15:26:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C56). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; same-resolution security |
| 2 | PASS | A crossover of two moving averages |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and the commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`basis_len` [18, 36] x `alma_offset` [0.88, 0.5]: **4 trials**; sigma 1 fixed; shorts off as the default.

## Ambiguities resolved

- Previous-bar comparison as written (one extra bar of delay). Trend lines are plots only. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
