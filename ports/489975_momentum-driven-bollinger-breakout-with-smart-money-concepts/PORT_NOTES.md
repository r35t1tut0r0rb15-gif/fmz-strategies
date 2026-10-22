# #489975 Momentum Driven Bollinger Breakout with Smart Money Concepts Integration Strategy -> `fmz_489975_bb55_breakout_structure_shift_momentum_candle_reversal`

- FMZ source id: 489975 (lineage).
- Source: https://www.fmz.com/strategy/489975 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-10 16:12:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C273). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger breakouts with structure-shift and momentum-candle filters |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 5 % of equity sizing stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [55, 20] x `momentum_body_percent` [0.7, 0.5]: **4 trials**; BB 2, swing 12, order block 20.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
