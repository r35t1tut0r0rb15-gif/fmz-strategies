# #491892 EMA双重交叉动态止损量化策略-EMA-Dual-Crossover-Dynamic-Stop-Loss-Quantitative-Strategy -> `fmz_491892_ema10_20_cross_ema50_side_ema10_exit_reversal`

- FMZ source id: 491892 (lineage).
- Source: https://www.fmz.com/strategy/491892 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-24 16:59:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C274). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with a trend filter and an EMA exit |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length10` [10, 5] x `length20` [20, 30]: **4 trials**; EMA 50.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
