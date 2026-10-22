# #473361 多时间框架RSI-EMA动量交易策略与头寸缩放-Multi-Timeframe-RSI-EMA-Momentum-Trading-Strategy-with-Position-Scaling -> `fmz_473361_rsi2_hook_ema_stack_rsi_exit_above_entry_reversal`

- FMZ source id: 473361 (lineage).
- Source: https://www.fmz.com/strategy/473361 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 15:23:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C217). Not run.

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

- Size doubling never fills (pyramiding 1). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
