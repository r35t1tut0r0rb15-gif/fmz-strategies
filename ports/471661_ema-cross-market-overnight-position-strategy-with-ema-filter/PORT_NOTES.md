# #471661 基于EMA指标的跨市场多空趋势隔夜持仓策略-Cross-Market-Overnight-Position-Strategy-with-EMA-Filter -> `fmz_471661_alternating_one_day_long_above_4h_ema100`

- FMZ source id: 471661 (lineage).
- Source: https://www.fmz.com/strategy/471661 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 10:49:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C209). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 4-hour values from completed bars |
| 2 | PASS | One-day longs above a 4-hour EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size, commission and slippage stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [100, 50]: **2 trials**; the EMA filter on.

## Ambiguities resolved

- Sessions unused (as written); 4-hour EMA from the last completed 4-hour bar. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
