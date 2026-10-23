# #430154 Multi indicator Decision Based Short Term Trend Strategy -> `fmz_430154_fib_pivot_cross_daily_vwap_stoch_rsi_cross_close_tp_reversal`

- FMZ source id: 430154 (lineage).
- Source: https://www.fmz.com/strategy/430154 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-25 15:31:30). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based target |
| 2 | PASS | Pivot / VWAP / stochastic-RSI confluence |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`take_profit` [0.01, 0.02] x `length_rsi` [14, 21]: **4 trials**; stochastic 14, K 3, D 3.

## Ambiguities resolved

- UTC day for the VWAP and pivots. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap_cross"`.

## Marks

`none`
