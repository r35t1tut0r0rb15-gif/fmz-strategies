# #482897 Multi Technical Indicator Moving Average Crossover Trend Following Quantitative Trading Strategy -> `fmz_482897_rsi_macd_stoch_bb_lower_to_basis_jump_reversal`

- FMZ source id: 482897 (lineage).
- Source: https://www.fmz.com/strategy/482897 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 16:56:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C253). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI / MACD / Stochastic / Bollinger confluence |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Lot size 0.1 and 1 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_period` [20, 40] x `rsi_period` [14, 7]: **4 trials**; MACD 12 / 26 / 9, Stochastic 14, band 2 sd.

## Ambiguities resolved

- REVERSAL INTENDED, no other exit. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
