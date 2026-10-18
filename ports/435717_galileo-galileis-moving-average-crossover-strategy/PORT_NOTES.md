# #435717 Galileo Galileis Moving Average Crossover Strategy -> `fmz_435717_open_ema_close_cross`

- FMZ source id: 435717 (lineage).
- Source: https://www.fmz.com/strategy/435717 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-18 12:07:07). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C80). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The cash order size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [11, 21]: **2 trials**.

## Ambiguities resolved

- Rising / falling close decides the side. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
