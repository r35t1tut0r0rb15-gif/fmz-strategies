# #437376 Nine Types of Moving Average Crossover Strategy -> `fmz_437376_ma_type_cross`

- FMZ source id: 437376 (lineage).
- Source: https://www.fmz.com/strategy/437376 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-02 10:37:21). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C99). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crossing |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_type` ["SMA", "EMA"] x `short_len` [5, 10]: **4 trials**; long 15, ALMA 0.85 / 6, LSMA offset 0 fixed; SL / PT off.

## Ambiguities resolved

- VWMA type left out (volume); SL / PT off and not ported. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
