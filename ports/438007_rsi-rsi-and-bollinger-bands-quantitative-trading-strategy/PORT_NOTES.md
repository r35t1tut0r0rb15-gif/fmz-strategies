# #438007 RSI与布林线量化交易策略RSI-and-Bollinger-Bands-Quantitative-Trading-Strategy -> `fmz_438007_bb_rsi_dip_buy_green_close`

- FMZ source id: 438007 (lineage).
- Source: https://www.fmz.com/strategy/438007 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-08 10:16:22). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C107). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger band and RSI levels; bar colour |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity lot, pyramiding 5 and the percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsilimit` [30, 20] x `bbperiod` [20, 40]: **4 trials**; BB mult 2 and RSI 7 fixed.

## Ambiguities resolved

- Zero-quantity short closes the long; pyramiding adds not held. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
