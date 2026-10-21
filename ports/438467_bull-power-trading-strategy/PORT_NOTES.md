# #438467 Bull Power Trading Strategy -> `fmz_438467_bull_power_level_state`

- FMZ source id: 438467 (lineage).
- Source: https://www.fmz.com/strategy/438467 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-12 12:02:49). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C110). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit levels -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND437644. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sell_frac` [0.00095, 0.01] x `buy_ratio` [0.075, 0.5]: **4 trials**; reverse off.

## Ambiguities resolved

- Price-unit levels -> fractions of the close (as #437644). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
