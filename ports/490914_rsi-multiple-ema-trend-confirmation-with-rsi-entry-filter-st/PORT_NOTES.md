# #490914 多重指数移动平均线趋势确认与RSI过滤入场策略-Multiple-EMA-Trend-Confirmation-with-RSI-Entry-Filter-Strategy -> `fmz_490914_four_ema_stack_rsi_cap_long`

- FMZ source id: 490914 (lineage).
- Source: https://www.fmz.com/strategy/490914 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-17 14:33:40). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMAs and an oscillator |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted (the commission is a cost, not in the module). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_cap` [60, 70] x `ema_mid` [63, 50]: **4 trials**; defaults 60 / 63 (the source's); EMA 9 / 21 / 200, RSI 14 fixed.

## Ambiguities resolved

- Commented-out exits are not code. Long only. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
