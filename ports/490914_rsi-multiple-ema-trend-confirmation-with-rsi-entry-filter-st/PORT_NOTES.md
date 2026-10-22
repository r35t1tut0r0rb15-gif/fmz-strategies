# #490914 多重指数移动平均线趋势确认与RSI过滤入场策略-Multiple-EMA-Trend-Confirmation-with-RSI-Entry-Filter-Strategy -> `fmz_490914_ema9_21_63_200_stack_rsi60_ema21_63_exit_long`

- FMZ source id: 490914 (lineage).
- Source: https://www.fmz.com/strategy/490914 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-17 14:33:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C274). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA-stack state with an RSI cap and an EMA-cross exit |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity, capital and commission stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_cap` [60, 70] x `exit_slow` [63, 100]: **4 trials**; EMA 9 / 21 / 200.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
