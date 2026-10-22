# #454738 Triple Standard Deviation Momentum Reversal Trading Strategy -> `fmz_454738_three_sd_band_reentry_long`

- FMZ source id: 454738 (lineage).
- Source: https://www.fmz.com/strategy/454738 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-21 14:44:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C196). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Three-deviation band re-entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [3.0, 2.0]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
