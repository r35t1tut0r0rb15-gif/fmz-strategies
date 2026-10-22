# #489311 Dynamic Trend Identification Strategy with Exponential Moving Average and Adaptive Volatility Threshold -> `fmz_489311_ema30_60_gap_adx_atr_margin_state_long`

- FMZ source id: 489311 (lineage).
- Source: https://www.fmz.com/strategy/489311 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-03 13:08:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C271). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA gap states with an ADX-dependent ATR margin |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG489311. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atrMultStrong` [0.3, 0.6] x `emaFastLen` [30, 15]: **4 trials**; EMA 60, ATR 60, ADX 14 / 20, weak 0.1.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
