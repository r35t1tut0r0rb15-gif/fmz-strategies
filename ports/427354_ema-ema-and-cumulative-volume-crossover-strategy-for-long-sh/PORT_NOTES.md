# #427354 基于EMA和累积成交量的多空交易策略EMA-and-Cumulative-Volume-Crossover-Strategy-for-Long-Short -> `fmz_427354_ema50_rolling_vwap100_cross_long_close_stop`

- FMZ source id: 427354 (lineage).
- Source: https://www.fmz.com/strategy/427354 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-20 11:48:34). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based stop |
| 2 | PASS | EMA against a rolling VWAP |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity x 10 % / (close x 8 %), 20 % of equity, capital 10000 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [50, 20] x `cumulative_period` [100, 50]: **4 trials**; stop 8 %.

## Ambiguities resolved

- position_size >= 1 read as in a position (weird case). Volume = broker tick volume. Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap_cross"`.

## Marks

`none`
