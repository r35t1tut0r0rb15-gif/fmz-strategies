# #453659 VWAP交易策略与成交量异常监测VWAP-Trading-Strategy-with-Volume-Anomaly-Detection -> `fmz_453659_four_anchored_vwaps_retest_rsi_exit_4h_reversal`

- FMZ source id: 453659 (lineage).
- Source: https://www.fmz.com/strategy/453659 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-07 15:44:04). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Wick and cross re-tests of four anchored VWAPs, RSI exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vol_thresh` [2.0, 3.0] x `rsi_ob` [70.0, 80.0]: **4 trials**; RSI oversold = 100 - overbought, volume SMA 20.

## Ambiguities resolved

- Data-start dependent anchors as written; last entry call wins. Volume = broker tick volume (VWAPs). REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap_breakout"`.

## Marks

`none`
