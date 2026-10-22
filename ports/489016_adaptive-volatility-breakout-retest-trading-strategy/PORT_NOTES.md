# #489016 Adaptive Volatility Breakout Retest Trading Strategy -> `fmz_489016_sma200_cross_retest5_atr1_bracket_reversal`

- FMZ source id: 489016 (lineage).
- Source: https://www.fmz.com/strategy/489016 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-01 10:54:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C268). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | SMA 200 crossings with a retest filter and an ATR bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`riskFactor` [1.0, 2.0] x `ma_length` [200, 100]: **4 trials**; retest 5, ATR 14.

## Ambiguities resolved

- Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
