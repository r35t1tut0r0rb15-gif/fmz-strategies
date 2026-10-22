# #439984 双移动平均线与StochRSI交叉的趋势追踪策略BlackBit-Trader-XO-Macro-Trend-Scanner-Strategy -> `fmz_439984_xo_trend_scanner_first_bar_bracket`

- FMZ source id: 439984 (lineage).
- Source: https://www.fmz.com/strategy/439984 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-25 15:21:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C128). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | EMA run starts, MACD histogram and EMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`takeprofit` [0.003, 0.01] x `stoploss` [0.0016, 0.005]: **4 trials**; EMA 12 / 25, MACD 26 / 100 / 9 and EMA 200 fixed.

## Ambiguities resolved

- Percent bracket from the fill. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
