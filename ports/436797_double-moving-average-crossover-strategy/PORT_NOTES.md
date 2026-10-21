# #436797 Double Moving Average Crossover Strategy -> `fmz_436797_psar_alma_cross`

- FMZ source id: 436797 (lineage).
- Source: https://www.fmz.com/strategy/436797 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-27 17:45:43). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C96). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SAR side and an average crossing |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`window` [50, 30] x `sigma` [6.0, 4.0]: **4 trials**; offset 0.85 and SAR 0.02 / 0.02 / 0.2 fixed.

## Ambiguities resolved

- Signals only, reversing. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
