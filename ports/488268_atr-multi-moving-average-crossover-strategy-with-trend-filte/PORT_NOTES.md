# #488268 趋势过滤多均线交叉ATR风控量化策略-Multi-Moving-Average-Crossover-Strategy-with-Trend-Filter-and-ATR-Risk-Management -> `fmz_488268_sma20_ema89_cross_sma200_side_atr_bracket_flat`

- FMZ source id: 488268 (lineage).
- Source: https://www.fmz.com/strategy/488268 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 13:42:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C265). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | MA crossings with a long-SMA filter and an ATR bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Strategy(): capital 10000 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stopLossMultiplier` [2.0, 1.5] x `takeProfitMultiplier` [3.0, 4.5]: **4 trials**; SMA 20, EMA 89, SMA 200, ATR 14.

## Ambiguities resolved

- Entries only from flat (a loop follows the bracket on the bar's high / low). FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
