# #426780 Stochastic Oscillator Band Breakout Strategy -> `fmz_426780_stochastic_bands`

- Source: https://www.fmz.com/strategy/426780 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-14 15:31:25). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [7, 14] x `up_band` [20, 50] x `down_band` [80, 50]: **8 trials**, defaults 7 / 20 / 80 (the source's).

## Ambiguities resolved

- Kept as written: the long test (%K > 20) comes first, so shorts only fire at %K <= 20 (bands look swapped: decision owed).
- %D only plots; "Trade reverse" off.
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks (2026-10-07)

`none`
