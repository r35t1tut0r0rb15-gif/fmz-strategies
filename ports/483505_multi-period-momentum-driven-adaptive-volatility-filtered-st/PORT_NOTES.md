# #483505 Multi Period Momentum Driven Adaptive Volatility Filtered Strategy -> `fmz_483505_composite_momentum_turn_vol_ceiling_5_15pct_bracket_long`

- FMZ source id: 483505 (lineage).
- Source: https://www.fmz.com/strategy/483505 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-24 09:38:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C259). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | Composite momentum turns with a volatility ceiling |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss` [0.05, 0.03] x `take_profit` [0.15, 0.1]: **4 trials**; periods 63 / 126 / 189 / 252, volatility ceiling 0.5, momentum threshold 0.

## Ambiguities resolved

- Periods and annualisation are in chart bars, as written. The bracket is ported from the fill. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
