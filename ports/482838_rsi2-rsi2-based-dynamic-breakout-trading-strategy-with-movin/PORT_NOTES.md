# #482838 基于RSI2的动态突破交易策略结合移动平均线过滤系统-RSI2-Based-Dynamic-Breakout-Trading-Strategy-with-Moving-Average-Filter-System -> `fmz_482838_rsi2_turn_up_sma50_time_exit_long`

- FMZ source id: 482838 (lineage).
- Source: https://www.fmz.com/strategy/482838 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:37:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI, a moving average and a bar count. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`max_bars` [5, 10] x `use_ma_filter` [True, False]: **4 trials**; defaults 5 / True (the source's); RSI 2, the 25
level and SMA 50 fixed.

## Ambiguities resolved

- The bar count starts on the signal bar, so the close is signalled 4 bars after it, as written. Entries only from
  flat while no count runs. Long only: opposite entries cannot occur. No stops.
- Broker days stamped with their first minute (as #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
