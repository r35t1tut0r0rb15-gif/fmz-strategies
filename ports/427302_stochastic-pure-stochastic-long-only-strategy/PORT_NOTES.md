# #427302 Pure Stochastic Long Only Strategy -> `fmz_427302_pure_stochastic_long`

- FMZ source id: 427302 (lineage).
- Source: https://www.fmz.com/strategy/427302 (PineScript (no @version line, v1 syntax), author ChaoZhang, FMZ last
  modified 2023-09-19 21:22:11). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels, price comparisons. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 14] x `over_sold` [20, 30] x `over_bought` [80, 70]: **8 trials**; defaults 10 / 20 / 80 (the source's); K 7, D 4, EMA 5 fixed; the middle level follows (OB + OS) / 2.

## Ambiguities resolved

- Long only, entries from flat; one signal per bar. FREQ = "5min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
