# #471689 High Win Rate Trend Mean Reversion Trading Strategy -> `fmz_471689_bb20_rsi_extreme_atr_bracket_reversal_2d`

- FMZ source id: 471689 (lineage).
- Source: https://www.fmz.com/strategy/471689 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 14:45:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C209). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at entry |
| 2 | PASS | Band and RSI extremes with a tight ATR bracket |
| 3 | PASS | Exchange pair in the header only (gold named in the title). |
| 4 | DONE | Equity-risk quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 50] x `rr` [0.75, 1.5]: **4 trials**; the 1 ATR stop and RSI levels fixed.

## Ambiguities resolved

- Opening bracket kept while signals repeat (trailing_stop_pending). REVERSAL INTENDED. FREQ = "2D".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
