# #437040 Trailing Stop Loss Dual Moving Average Strategy -> `fmz_437040_sma_cross_trailing_sell_long`

- FMZ source id: 437040 (lineage).
- Source: https://www.fmz.com/strategy/437040 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-29 16:59:17). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C99). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trailing level is tested on closes |
| 2 | PASS | Percent trailing level |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [21, 10] x `dev` [0.03, 0.05]: **4 trials**; slow 49 and the low as exit control fixed.

## Ambiguities resolved

- Close-tested trailing sell as an exit signal; barssince / nz placeholders as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
