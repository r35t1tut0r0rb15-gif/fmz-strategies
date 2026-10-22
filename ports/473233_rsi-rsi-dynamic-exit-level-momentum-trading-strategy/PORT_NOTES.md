# #473233 RSI动态平仓位动量交易策略-RSI-Dynamic-Exit-Level-Momentum-Trading-Strategy -> `fmz_473233_rsi30_70_cross_rsi60_40_closes_call_order`

- FMZ source id: 473233 (lineage).
- Source: https://www.fmz.com/strategy/473233 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 14:59:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C214). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI threshold crossings with RSI close levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `close_long` [60, 70] x `close_short` [40, 30]: **8 trials**.

## Ambiguities resolved

- Written call order (long to short reversal only on a closing bar). REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
