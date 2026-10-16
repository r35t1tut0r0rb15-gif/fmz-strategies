# #427893 Relative Volatility Index Backtesting Strategy -> `fmz_427893_hpotter_relative_volatility_index`

- FMZ source id: 427893 (lineage).
- Source: https://www.fmz.com/strategy/427893 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-26 16:15:44). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C13). Not run.
- Near-duplicate group: **ND427893** (2 members, best partner #436644, Jaccard 0.757); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427893. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [10, 5, 20, 30]: **4 trials**; default 10 (the source's); zones 30 / 70 fixed.

## Ambiguities resolved

- Population stdev; nz restarts the smoothing after the first na.
- "Trade reverse" fixed off. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
