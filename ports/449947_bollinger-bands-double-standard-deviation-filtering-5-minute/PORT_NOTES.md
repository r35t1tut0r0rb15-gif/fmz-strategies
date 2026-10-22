# #449947 Bollinger Bands Double Standard Deviation Filtering 5 Minute Quantitative Trading Strategy -> `fmz_449947_one_sd_band_reentry_reversal`

- FMZ source id: 449947 (lineage).
- Source: https://www.fmz.com/strategy/449947 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-30 16:03:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C182). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | One-sd band re-entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `k` [1.0, 1.5]: **4 trials**.

## Ambiguities resolved

- Previous close against the current band, as written. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
