# #481367 基于EMA交叉结合RSIADX和成交量确认的动态止盈止损系统-Dynamic-Stop-Loss-and-Take-Profit-System-Based-on-EMA-Crossover-with-RSI-ADX-and-Volume-Confirmation -> `fmz_481367_ema9_21_rsi_adx_volume_loose_short_avg_bracket_3h_reversal`

- FMZ source id: 481367 (lineage).
- Source: https://www.fmz.com/strategy/481367 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-10 15:10:20). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; position-price bracket followed in the signals |
| 2 | PASS | EMA crossings with RSI / volume / ADX filters, loose short state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.03, 0.02] x `tp` [0.05, 0.08]: **4 trials**; EMA 9 / 21, RSI 14, DMI 14 / 14, volume SMA 20.

## Ambiguities resolved

- Operator precedence makes the short a near-state. Bracket followed at the next open. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
