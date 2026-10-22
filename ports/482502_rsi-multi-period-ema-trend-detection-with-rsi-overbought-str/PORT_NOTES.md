# #482502 多周期均线趋势判断与RSI超买策略-Multi-Period-EMA-Trend-Detection-with-RSI-Overbought-Strategy -> `fmz_482502_close_ema20_cross_rising_ema_stack_rsi70_exit_long`

- FMZ source id: 482502 (lineage).
- Source: https://www.fmz.com/strategy/482502 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 17:50:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C246). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA 20 re-crossings in a rising EMA stack with RSI / EMA exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_exit` [70, 80] x `ema_entry` [20, 10]: **4 trials**; EMA 50 / 100 rising, RSI 14.

## Ambiguities resolved

- Long only. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
