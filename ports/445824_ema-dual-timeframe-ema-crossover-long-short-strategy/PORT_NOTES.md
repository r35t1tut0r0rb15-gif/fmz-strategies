# #445824 基于双时间框架EMA交叉信号的多空策略Dual-Timeframe-EMA-Crossover-Long-Short-Strategy -> `fmz_445824_2h_ema_order_3m_sampled_cross_reversal`

- FMZ source id: 445824 (lineage).
- Source: https://www.fmz.com/strategy/445824 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-22 15:01:39). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C173). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the 2-hour and 3-minute values end with the daily bar |
| 2 | PASS | EMA order with sampled lower-time-frame crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_ema` [5, 9] x `long_ema` [20, 50]: **4 trials**; the two time frames fixed.

## Ambiguities resolved

- Last 2-hour / 3-minute bar of each broker day. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`
