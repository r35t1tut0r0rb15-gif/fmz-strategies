# #432347 Mean Reversion Trading Strategy Based on Bollinger Bands and Golden Ratio -> `fmz_432347_vwma50_bb_fib618_dip_ema_uptrend_close_stop_long`

- FMZ source id: 432347 (lineage).
- Source: https://www.fmz.com/strategy/432347 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-16 16:52:55). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based stop in the signals |
| 2 | PASS | Bollinger 0.618 band mean reversion in an EMA uptrend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 20 % of equity, capital 10000, pyramiding 1, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 20] x `mult` [1.5, 2.0]: **4 trials**; band 0.618, EMA 50 / 200, close stop 5 %.

## Ambiguities resolved

- position_size >= 1 read as in a position; close-based stop at the fill price. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
