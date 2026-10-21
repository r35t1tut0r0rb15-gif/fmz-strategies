# #439082 Improved SuperTrend Strategy -> `fmz_439082_sma_atr_band_line_stochrsi`

- FMZ source id: 439082 (lineage).
- Source: https://www.fmz.com/strategy/439082 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-17 15:55:15). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C116). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band line crossings and Stochastic RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 3.0] x `filter_len` [5, 10]: **4 trials**; ATR 14 and Stochastic RSI 14 / 3 fixed.

## Ambiguities resolved

- Down test overrides the up test; reversal stands. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
