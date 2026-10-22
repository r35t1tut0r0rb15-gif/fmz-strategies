# #446984 Multi Indicator Trend Following Dynamic Risk Management Strategy -> `fmz_446984_macd_cross_ema50_200_trend_rsi_atr_bracket_reversal`

- FMZ source id: 446984 (lineage).
- Source: https://www.fmz.com/strategy/446984 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-03 17:40:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C177). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed on the signal bar (re-sent levels marked) |
| 2 | PASS | MACD crossings with trend and RSI filters, ATR bracket |
| 3 | PASS | No exchange header. |
| 4 | DONE | The risk quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_mult` [3.0, 1.5] x `rr` [2.0, 1.5]: **4 trials**; the MACD, RSI, EMA and ATR lengths fixed.

## Ambiguities resolved

- No bar size in the source (bar_size_pending); levels from the signal bar. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`bar_size_pending, trailing_stop_pending`
