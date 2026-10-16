# #430117 Momentum Arbitrage Strategy Backtest Analysis -> `fmz_430117_cmo_bands`

- FMZ source id: 430117 (lineage).
- Source: https://www.fmz.com/strategy/430117 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-25 11:10:59). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A bounded momentum oscillator. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430117. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [9, 14, 20] x `band` [70, 50]: **6 trials**; bands +-band.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
