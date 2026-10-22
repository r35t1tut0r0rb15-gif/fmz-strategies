# #488523 多重均线回归MACD趋势确认策略-Multiple-EMA-Reversion-MACD-Trend-Confirmation-Strategy -> `fmz_488523_macd_cross_ema20_250_ema2_pullback_atr5_bracket_reversal`

- FMZ source id: 488523 (lineage).
- Source: https://www.fmz.com/strategy/488523 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-28 15:40:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C267). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | MACD crossings with EMA trend and pullback filters |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atrMultiplier` [5.0, 2.5] x `rrRatio` [1.5, 3.0]: **4 trials**; EMA 20 / 250 / 2 / 100 / 300, MACD 12 / 26 / 9, ATR 14.

## Ambiguities resolved

- Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`trailing_stop_pending`
