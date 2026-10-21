# #438067 Dual Moving Average Crossover and Bull Bear Power Balance Combination Strategy -> `fmz_438067_ema2_20_bull_bear_balance_combo`

- FMZ source id: 438067 (lineage).
- Source: https://www.fmz.com/strategy/438067 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-08 17:09:48). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C109). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit levels -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND429466. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 20] x `level_atr` [0.015, 0.25]: **4 trials**; reverse off.

## Ambiguities resolved

- Price-unit balance levels -> ATR fractions (as #430899). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
