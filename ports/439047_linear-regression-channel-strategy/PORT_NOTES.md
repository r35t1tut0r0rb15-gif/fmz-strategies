# #439047 Linear Regression Channel Strategy -> `fmz_439047_linreg_band_dip_hull_long`

- FMZ source id: 439047 (lineage).
- Source: https://www.fmz.com/strategy/439047 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-17 11:41:16). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C115). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Regression band and Hull filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [55, 100] x `hma_len` [400, 200]: **4 trials**; band -2 % fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
