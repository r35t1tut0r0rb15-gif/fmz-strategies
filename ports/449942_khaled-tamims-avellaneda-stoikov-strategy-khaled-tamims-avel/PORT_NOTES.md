# #449942 Khaled Tamims Avellaneda Stoikov Strategy Khaled Tamims Avellaneda Stoikov Strategy -> `fmz_449942_avellaneda_stoikov_mid_band_reversion_reversal`

- FMZ source id: 449942 (lineage).
- Source: https://www.fmz.com/strategy/449942 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-30 15:54:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C181). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | One-bar moves beyond a fixed band around the mid price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`band_frac` [0.00128, 0.005]: **2 trials**; the fee 0 fixed, as written.

## Ambiguities resolved

- Price-unit band as 0.00128 of the price. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
