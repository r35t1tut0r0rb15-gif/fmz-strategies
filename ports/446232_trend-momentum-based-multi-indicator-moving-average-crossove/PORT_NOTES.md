# #446232 Trend Momentum Based Multi Indicator Moving Average Crossover Strategy -> `fmz_446232_sma50_rsi_macd_six_ids_call_order_reversal`

- FMZ source id: 446232 (lineage).
- Source: https://www.fmz.com/strategy/446232 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-26 17:17:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C174). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA, RSI and MACD entries in call order |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow` [50, 100] x `rsi_len` [14, 7]: **4 trials**; the RSI levels and the MACD fixed.

## Ambiguities resolved

- The Short id fires on the buy crossing, as written; call order with ids tracked. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
