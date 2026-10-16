# #430380 Classic Dual Moving Average Crossover Strategy -> `fmz_430380_stochastic_biznesfilosof`

- FMZ source id: 430380 (lineage).
- Source: https://www.fmz.com/strategy/430380 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-27 16:47:30). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Stochastic levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out 20 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 14] x `bottom` [14, 20]: **4 trials**; upper = 100 - bottom; smoothing 3 / 3 fixed.

## Ambiguities resolved

- An opposite signal while in a position ends the bar flat (close_all after the entry). FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
