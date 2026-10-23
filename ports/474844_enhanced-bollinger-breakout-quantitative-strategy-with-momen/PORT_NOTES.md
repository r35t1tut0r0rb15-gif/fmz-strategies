# #474844 Enhanced Bollinger Breakout Quantitative Strategy with Momentum Filter Integration System -> `fmz_474844_confirmed_bollinger_breakout_ema200_volume_atr_bracket_2d_reversal`

- FMZ source id: 474844 (lineage).
- Source: https://www.fmz.com/strategy/474844 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 14:55:37). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | Confirmed Bollinger breakouts in the EMA 200 trend on volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`confirm` [2, 1] x `rr` [1.5, 2.0]: **4 trials**; BB 20 x 2, RSI 14, EMA 200, ATR 14 x 1.5.

## Ambiguities resolved

- Bracket at the first signal's close; repeats re-send it (pending). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "2D".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
