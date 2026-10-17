# #435234 Reverasal Indicator Strategy -> `fmz_435234_cci_cross_rsi_extreme_turn`

- FMZ source id: 435234 (lineage).
- Source: https://www.fmz.com/strategy/435234 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-13 14:45:51). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C75). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | CCI, RSI and an average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cci_len` [10, 20] x `ob` [65, 75]: **4 trials**; the oversold level is 100 minus the overbought one; RSI 14 and EMA 100 fixed.

## Ambiguities resolved

- Any-direction zero cross, as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
