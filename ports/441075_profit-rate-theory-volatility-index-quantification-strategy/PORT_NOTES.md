# #441075 Profit rate theory volatility index quantification strategy -> `fmz_441075_tradingview_technical_rating_atr_stop_3h_reversal`

- FMZ source id: 441075 (lineage).
- Source: https://www.fmz.com/strategy/441075 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-05 13:54:34). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR stop from the signal bar as a fraction of the fill |
| 2 | PASS | TradingView technical-rating thresholds |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, commission 0.1 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bound` [0.5, 0.3] x `sl_atr` [3.0, 2.0]: **4 trials**; all rating components fixed.

## Ambiguities resolved

- Rating recipe as written; ATR stop fixed at the signal bar, trail not followed. Volume = broker tick volume (VWMA vote). REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "indicator_vote"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
