# #482450 动态EMA交叉与RSI协同交易系统-Dynamic-EMA-Crossover-with-RSI-Synergy-Trading-System -> `fmz_482450_ema9_21_cross_rsi50_point_bracket_atr`

- FMZ source id: 482450 (lineage).
- Source: https://www.fmz.com/strategy/482450 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 14:57:55). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | EMAs, RSI and ATR multiples; the point distances converted. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Lot size and the INR risk arithmetic quoted; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.1, 1.0] x `tp_atr` [0.5, 2.0]: **4 trials**; defaults 0.1 / 0.5 (the source's 25 / 125 points read on
Nifty); EMA 9 / 21, RSI 14 and ATR 14 fixed.

## Ambiguities resolved

- 25 / 125 points are price units: absurd on BTC_USDT daily bars, so judged on the Nifty index the script's comments
  name (daily ATR about 250 points): 0.1 / 0.5 ATR (as #489333). The 1.0 / 2.0 ATR pair is the declared variant.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). Daily bars: broker days stamped with their first
  minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`
