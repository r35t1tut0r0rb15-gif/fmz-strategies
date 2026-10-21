# #438032 DEMA与EMA交叉结合ATR波动率的短期策略Momentum-Strategy-Based-on-DEMA-and-EMA-Crossover-with-ATR-Volatility-Filter -> `fmz_438032_dema_ema_cross_short_held`

- FMZ source id: 438032 (lineage).
- Source: https://www.fmz.com/strategy/438032 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-08 14:14:57). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C108). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; higher-timeframe values from completed days |
| 2 | PASS | DEMA / EMA crossing and an ATR-percent filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `ema_len` [25, 50]: **4 trials**; ATR 14 and the EMA 20 filter fixed.

## Ambiguities resolved

- The exit is gated on a long position and never sent: one short held. Short only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
