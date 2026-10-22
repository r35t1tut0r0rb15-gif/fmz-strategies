# #458054 Multi Indicator Comprehensive Trading Strategy Perfect Combination of Momentum Overbought Oversold and Volatility -> `fmz_458054_macd_or_rsi_trigger_inside_bands_bracket_reversal`

- FMZ source id: 458054 (lineage).
- Source: https://www.fmz.com/strategy/458054 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 15:45:39). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C200). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the bracket as fixed fractions; re-issued levels pending (mark) |
| 2 | PASS | MACD / RSI triggers inside the bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `sl_pct` [0.02, 0.01] x `tp_pct` [0.05, 0.03]: **8 trials**; the MACD and band settings fixed.

## Ambiguities resolved

- Re-issued levels pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`trailing_stop_pending`
