# #439833 Dynmaic Risk Adjusted Momentum Trading Strategy -> `fmz_439833_normalised_price_hma_cross_range_stop`

- FMZ source id: 439833 (lineage).
- Source: https://www.fmz.com/strategy/439833 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-24 11:13:39). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C125). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR stop from the signal bar |
| 2 | PASS | Normalised price and its HMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The volatility-target size, leverage and compounding stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hlength` [100, 50] x `stop_multiple` [1.0, 2.0]: **4 trials**; normalisation 14 fixed.

## Ambiguities resolved

- Stop from the signal bar's average range. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`coarse_bar_stop`
