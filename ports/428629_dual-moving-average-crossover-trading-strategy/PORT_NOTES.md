# #428629 Dual Moving Average Crossover Trading Strategy -> `fmz_428629_distance_oscillator_hma`

- FMZ source id: 428629 (lineage).
- Source: https://www.fmz.com/strategy/428629 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-07 16:39:01). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Percent distance and MA lengths. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 25] x `lagg` [12, 6]: **4 trials**; defaults 50 / 12 (the source's); channel 20 fixed.

## Ambiguities resolved

- Percent format and Hull average (defaults). REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
