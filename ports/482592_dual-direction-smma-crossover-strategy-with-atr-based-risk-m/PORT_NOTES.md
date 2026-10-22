# #482592 Dual-Direction-SMMA-Crossover-Strategy-with-ATR-Based-Risk-Management-and-Fixed-Take-Profit-双向SMMA交叉ATR风控定向获利策略 -> `fmz_482592_smma17_cross_point_target_reversal`

- FMZ source id: 482592 (lineage).
- Source: https://www.fmz.com/strategy/482592 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-19 10:59:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C247). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; point targets as fractions of the fill; SMMA stop described (pending) |
| 2 | PASS | SMMA crossings with fixed targets |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`smma_length` [17, 34] x `tp_scale` [1.0, 2.0]: **4 trials**; targets 1150 / 1500 points (fractions of 42000) x scale.

## Ambiguities resolved

- The points are price amounts (fractions of 42000). The SMMA / ATR stop is pending.
- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
