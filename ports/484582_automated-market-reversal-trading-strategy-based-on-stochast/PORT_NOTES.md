# #484582 Automated Market Reversal Trading Strategy Based on Stochastic Indicator and Candlestick Patterns -> `fmz_484582_candle_reversals_stoch_zone_atr_bracket_reversal`

- FMZ source id: 484582 (lineage).
- Source: https://www.fmz.com/strategy/484582 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-03 10:03:52). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C261). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | Candle reversals in Stochastic extreme zones |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`thresh` [80.0, 70.0] x `trend_len` [14, 20]: **4 trials**; ATR 14, target 1.5 ATR, stop 1 ATR, smoothing 20.

## Ambiguities resolved

- Tick-rounded equality tests compare the stored prices directly. A repeat signal's re-sent bracket is pending.
- MPL 2.0 source, ported and stated. REVERSAL INTENDED. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`trailing_stop_pending`
