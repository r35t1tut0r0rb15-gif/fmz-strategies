# #478720 Multi Smoothed Moving Average Dynamic Crossover Trend Following Strategy with Multiple Confirmations -> `fmz_478720_triple_ema7_signal12_cross_filters_atr_bracket_reversal`

- FMZ source id: 478720 (lineage).
- Source: https://www.fmz.com/strategy/478720 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-17 15:53:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C239). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | Triple-smoothed MA crossings with trend, momentum and volatility filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slength` [7, 14] x `siglen` [12, 24]: **4 trials**; EMA 200, RSI 14 / 50, ATR 14, SL 1.5 / TP 2 ATR.

## Ambiguities resolved

- Repeat-signal re-sends not followed. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
