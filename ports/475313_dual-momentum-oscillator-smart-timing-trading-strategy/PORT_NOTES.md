# #475313 Dual Momentum Oscillator Smart Timing Trading Strategy -> `fmz_475313_rsi35_stoch20_dip_rsi70_stoch80_exit_long`

- FMZ source id: 475313 (lineage).
- Source: https://www.fmz.com/strategy/475313 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-17 14:36:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C228). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI / stochastic extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG475313. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_buy` [35, 30] x `stoch_buy` [20, 10]: **4 trials**; the sell levels fixed.

## Ambiguities resolved

- Weekly data off (default). Long only.

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
