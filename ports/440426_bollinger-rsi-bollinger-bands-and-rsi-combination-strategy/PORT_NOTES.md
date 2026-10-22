# #440426 收缩带Bollinger与RSI组合策略Bollinger-Bands-and-RSI-Combination-Strategy -> `fmz_440426_boll_squeeze_rsi_slope_atr_line`

- FMZ source id: 440426 (lineage).
- Source: https://www.fmz.com/strategy/440426 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-30 15:15:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C134). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested trailing line |
| 2 | PASS | ATR / Bollinger squeeze and RSI slopes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 14] x `overbought` [70, 80]: **4 trials**; the BB / ATR multiplier 2 fixed.

## Ambiguities resolved

- Close-tested trailing line; date window dropped. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_squeeze"`.

## Marks

`none`
