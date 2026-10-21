# #437558 Grid Trading Strategy Based on Moving Average System -> `fmz_437558_noro_fishnet_jma_trend`

- FMZ source id: 437558 (lineage).
- Source: https://www.fmz.com/strategy/437558 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-03 17:18:22). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C102). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average comparison |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity-based lot stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_len` [10, 20] x `slow_len` [200, 100]: **4 trials**; colour filter off.

## Ambiguities resolved

- nz-seeded recursions as written; state entries. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
