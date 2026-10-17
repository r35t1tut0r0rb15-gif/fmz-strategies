# #482592 Dual-Direction-SMMA-Crossover-Strategy-with-ATR-Based-Risk-Management-and-Fixed-Take-Profit-双向SMMA交叉ATR风控定向获利策略 -> `fmz_482592_smma17_cross_atr_stop_atr_target`

- FMZ source id: 482592 (lineage).
- Source: https://www.fmz.com/strategy/482592 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-19 10:59:14). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving stop fixed at entry (marked). |
| 2 | PASS | An SMMA and ATR multiples; the point targets converted. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_atr` [0.75, 1.5] x `smma_len` [17, 34]: **4 trials**; defaults 0.75 / 17 (the source's); ATR 14 and the
1.2 / 1.5 ATR targets fixed.

## Trailing stop (mark `trailing_stop_pending`)

`strategy.exit` runs every bar with the stop at the current SMMA -/+ 0.75 ATR, so it follows the average. The port
fixes it at the entry's signal bar (re-based on the fill).

## Ambiguities resolved

- 1150 / 1500 points on BTC_USDT 4-hour bars (2024-25, ATR about 900-1000) read as 1.2 / 1.5 ATR (criterion 2, as
  #489333).
- The closes repeat the reversal. REVERSAL INTENDED (always in). Stop module: `portfolio_kwargs` {} (D4).
  FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`, `trailing_stop_pending`
