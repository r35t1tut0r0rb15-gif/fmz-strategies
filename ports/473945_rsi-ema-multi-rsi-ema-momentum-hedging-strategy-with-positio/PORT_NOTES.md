# #473945 多重RSI-EMA动量对冲增仓策略-Multi-RSI-EMA-Momentum-Hedging-Strategy-with-Position-Scaling -> `fmz_473945_rsi2_hook_ema_stack_rsi_exit_above_entry_reversal_10min`

- FMZ source id: 473945 (lineage).
- Source: https://www.fmz.com/strategy/473945 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-04 15:41:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C220). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI 2 hooks in a counter-trend EMA stack, with an RSI exit above the entry price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Equity and leverage size stored, not ported (repeat entries blocked by pyramiding 1). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (all lengths and levels are constants).

## Ambiguities resolved

- Same rules as #473361. Size doubling never fills (pyramiding 1). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
