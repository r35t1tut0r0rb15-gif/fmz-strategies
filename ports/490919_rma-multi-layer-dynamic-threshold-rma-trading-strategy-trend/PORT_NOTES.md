# #490919 多层动态阈值RMA量化交易策略趋势与动量协同优化方法-Multi-Layer-Dynamic-Threshold-RMA-Trading-Strategy-Trend-and-Momentum-Synergy-Optimization -> `fmz_490919_rma9_21_50_stack_mid_cross_rma50_target_tick_stop_reversal`

- FMZ source id: 490919 (lineage).
- Source: https://www.fmz.com/strategy/490919 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-17 14:44:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C274). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; RMA / tick bracket as fractions of the fill |
| 2 | ADAPT | The tick stop read as a percent at the header price |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG490919. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.05, 0.5] x `midLen` [21, 34]: **4 trials**; RMA 9 / 50, RSI 8.

## Ambiguities resolved

- Ticks read at TRX 0.2; the RMA 50 target is under the price in a bullish stack, as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
