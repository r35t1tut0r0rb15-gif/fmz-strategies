# #458053 高精度RSI和布林带突破策略与优化风险比-High-Precision-RSI-and-Bollinger-Bands-Breakout-Strategy-with-Optimized-Risk-Reward-Ratio -> `fmz_458053_rsi_bollinger_extreme_volume_atr_1_5_bracket_1h_reversal`

- FMZ source id: 458053 (lineage).
- Source: https://www.fmz.com/strategy/458053 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 15:38:55). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | RSI / Bollinger extremes on above-average volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_ratio` [5.0, 2.0] x `sl_ratio` [1.0, 1.5]: **4 trials**; RSI 14, BB 20 x 2, ATR 14.

## Ambiguities resolved

- Bracket at the first signal's close. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
