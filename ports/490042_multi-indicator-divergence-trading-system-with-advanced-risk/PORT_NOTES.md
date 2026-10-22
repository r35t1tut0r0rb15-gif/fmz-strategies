# #490042 Multi Indicator Divergence Trading System with Advanced Risk Management -> `fmz_490042_rsi_macd_stoch_triple_cross_sma50_pct_bracket_trail_long`

- FMZ source id: 490042 (lineage).
- Source: https://www.fmz.com/strategy/490042 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-11 09:22:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C273). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill and a percent trail |
| 2 | ADAPT | The tick trail read as percents at the header price |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stopLossPercent` [1.5, 3.0] x `takeProfitPercent` [3.0, 6.0]: **4 trials**; trail 10 / 5 ticks at ETH 3000.

## Ambiguities resolved

- The stoch argument order and the tick trail are as written; ticks read at ETH 3000. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`trailing_stop`
