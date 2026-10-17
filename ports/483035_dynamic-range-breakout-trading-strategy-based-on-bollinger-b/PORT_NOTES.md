# #483035 基于布林带和相对强弱指数的动态区间突破交易策略-Dynamic-Range-Breakout-Trading-Strategy-Based-on-Bollinger-Bands-and-RSI -> `fmz_483035_bollinger_rsi_reentry_long_1d`

- FMZ source id: 483035 (lineage).
- Source: https://www.fmz.com/strategy/483035 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:17:13). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bollinger bands and RSI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [2.0, 2.5] x `rsi_ob` [70, 60]: **4 trials**; defaults 2 / 70 (the source's); BB 20, RSI 14 and the
1.5 x 30 entry filter fixed.

## Ambiguities resolved

- `ta.stdev` is the population standard deviation. Long only: opposite entries cannot occur. No stops.
- Broker days stamped with their first minute (as #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
