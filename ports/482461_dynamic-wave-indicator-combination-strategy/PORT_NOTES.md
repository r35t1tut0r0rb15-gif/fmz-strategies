# #482461 动态波浪指标组合策略-Dynamic-Wave-Indicator-Combination-Strategy -> `fmz_482461_macd_cross_ema200_adx_rsi_atr_rr`

- FMZ source id: 482461 (lineage).
- Source: https://www.fmz.com/strategy/482461 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 15:20:31). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | MACD, an EMA, ADX, RSI and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_min` [20, 25] x `rr` [2, 3]: **4 trials**; defaults 20 / 2 (the source's); MACD 12 / 26 / 9, EMA 200, RSI 14,
ADX 14 and the 1.5 ATR stop fixed.

## Ambiguities resolved

- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`
