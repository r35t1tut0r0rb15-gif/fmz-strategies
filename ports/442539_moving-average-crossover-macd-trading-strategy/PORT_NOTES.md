# #442539 Moving Average Crossover MACD Trading Strategy -> `fmz_442539_macd_cross_two_bar_confirm_reversal`

- FMZ source id: 442539 (lineage).
- Source: https://www.fmz.com/strategy/442539 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-22 16:25:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C157). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit delta floor -> fraction of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`confirm` [2, 1] x `fast` [12, 8]: **4 trials**; the slow and signal lengths and the delta floor fixed.

## Ambiguities resolved

- Delta floor as a fraction of the close; date window dropped. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
