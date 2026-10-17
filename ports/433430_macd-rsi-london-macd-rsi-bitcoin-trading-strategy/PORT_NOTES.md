# #433430 基于MACD和RSI的交易策略London-MACD-RSI-Bitcoin-Trading-Strategy -> `fmz_433430_london_macd_rsi`

- FMZ source id: 433430 (lineage).
- Source: https://www.fmz.com/strategy/433430 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-27 15:44:29). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C60). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; clock-time window |
| 2 | PASS | MACD crosses and RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tz` ["UTC", "Europe/London"] x `rsi_band` [35, 45]: **4 trials**; the long level is rsi_band, the short 100 - rsi_band.

## Ambiguities resolved

- Window in UTC (header) or London time, both declared. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
