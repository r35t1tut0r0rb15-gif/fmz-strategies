# #428696 双CCI滤波momentum爆发交易策略Dual-CCI-Filtered-Momentum-Explosion-Trading-Strategy -> `fmz_428696_ema_sma_cross_two_cci`

- FMZ source id: 428696 (lineage).
- Source: https://www.fmz.com/strategy/428696 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-08 14:10:41). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Sign tests and an RSI level only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cci_fast` [34, 20] x `rsi_level` [48, 50]: **4 trials**; EMA 8, SMA 26, momentum 5, CCI 55 and RSI 26 fixed.

## Ambiguities resolved

- CCI uses the mean absolute deviation (Pine's `cci`). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
