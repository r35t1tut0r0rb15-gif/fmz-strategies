# #458176 Multi Indicator Dynamic Volatility Alert Trading System -> `fmz_458176_bb20_extreme_macd_rsi_confirm_reversal`

- FMZ source id: 458176 (lineage).
- Source: https://www.fmz.com/strategy/458176 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 15:57:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C202). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band extremes with MACD and RSI confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 2.5]: **4 trials**; the MACD and RSI settings fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
