# #433441 Cross Moving Average Price Strategy -> `fmz_433441_noro_cross_ma_antisaw`

- FMZ source id: 433441 (lineage).
- Source: https://www.fmz.com/strategy/433441 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-27 16:52:19). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C60). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bars entirely above / below an average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The lot formula and the commission stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [30, 15, 60]: **3 trials**; SMA, offset 0 and anti-saw fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
