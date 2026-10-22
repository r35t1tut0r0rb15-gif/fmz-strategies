# #453235 Dual Moving Average Crossover Stop Loss and Take Profit Strategy -> `fmz_453235_ema5_200_cross_point_bracket_reversal`

- FMZ source id: 453235 (lineage).
- Source: https://www.fmz.com/strategy/453235 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 11:02:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C191). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the price-unit bracket as fractions of 42000 |
| 2 | PASS | EMA 5 / 200 crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_frac` [0.00119, 0.01] x `tp_frac` [0.00476, 0.02]: **4 trials**; the EMA lengths fixed.

## Ambiguities resolved

- Points as fractions of 42000. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
