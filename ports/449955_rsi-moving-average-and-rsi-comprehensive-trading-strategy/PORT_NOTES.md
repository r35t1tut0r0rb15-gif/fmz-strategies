# #449955 移动平均线与RSI综合交易策略-Moving-Average-and-RSI-Comprehensive-Trading-Strategy -> `fmz_449955_two_sma_pairs_rsi_extreme_four_ids_reversal`

- FMZ source id: 449955 (lineage).
- Source: https://www.fmz.com/strategy/449955 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-30 16:31:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C182). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Two SMA crossing pairs with RSI extremes, id-specific closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `ob` [70.0, 60.0]: **4 trials**; the SMA lengths and the oversold level fixed.

## Ambiguities resolved

- Call order with ids tracked. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
