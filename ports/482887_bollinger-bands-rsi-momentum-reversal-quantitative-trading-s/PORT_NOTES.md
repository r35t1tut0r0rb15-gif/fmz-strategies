# #482887 Bollinger-Bands与RSI结合的动量反转量化交易策略-Momentum-Reversal-Quantitative-Trading-Strategy-Combining-Bollinger-Bands-and-RSI -> `fmz_482887_bb20_2_reentry_rsi14_30_70_basis_exit_reversal`

- FMZ source id: 482887 (lineage).
- Source: https://www.fmz.com/strategy/482887 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 16:38:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C252). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger band re-entries with RSI extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `mult` [2.0, 1.5]: **4 trials**; RSI 14 / 30 / 70.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
