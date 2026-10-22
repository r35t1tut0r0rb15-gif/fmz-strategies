# #491897 Multi Factor Trend Following Quantitative Strategy -> `fmz_491897_psar_cross_ema2_rsi6_adx30_atr_bracket_reversal`

- FMZ source id: 491897 (lineage).
- Source: https://www.fmz.com/strategy/491897 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-24 17:23:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C274). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | SAR crossings with EMA / RSI / ADX filters and an ATR bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Risk-sized quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adxThreshold` [30, 20] x `atrMultiplier` [1.5, 2.5]: **4 trials**; SAR 0.02 / 0.2, EMA 2, RSI 6.

## Ambiguities resolved

- Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
