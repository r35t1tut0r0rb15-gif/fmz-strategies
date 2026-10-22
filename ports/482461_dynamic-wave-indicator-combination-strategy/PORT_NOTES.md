# #482461 Dynamic Wave Indicator Combination Strategy -> `fmz_482461_macd_cross_ema200_adx20_rsi50_atr_bracket_reversal`

- FMZ source id: 482461 (lineage).
- Source: https://www.fmz.com/strategy/482461 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 15:20:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C245). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | MACD crossings with trend, ADX and RSI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_threshold` [20, 25] x `risk_reward_ratio` [2, 3]: **4 trials**; MACD 12 / 26 / 9, EMA 200, ATR 14 x 1.5.

## Ambiguities resolved

- A repeat signal's re-sent bracket is pending. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
