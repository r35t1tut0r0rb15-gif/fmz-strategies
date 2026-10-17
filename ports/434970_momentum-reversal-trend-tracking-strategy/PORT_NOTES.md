# #434970 Momentum Reversal Trend Tracking Strategy -> `fmz_434970_trend_pullback_rsi_bb_macd`

- FMZ source id: 434970 (lineage).
- Source: https://www.fmz.com/strategy/434970 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-11 13:45:55). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C72). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Averages, RSI, bands and MACD |
| 3 | PASS |  |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_lvl` [30, 40] x `fast` [50, 20]: **4 trials**; the overbought level is 100 minus the oversold one; EMA 200, BB 20 / 2 and MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- No bar size (bar_size_pending). Symmetric RSI levels in the grid. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`bar_size_pending`
