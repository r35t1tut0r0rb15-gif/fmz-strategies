# #437693 基于EMA和SMA均线交叉的趋势反转策略Trend-Reversal-Strategy-Based-on-EMA-and-SMA-Crossover -> `fmz_437693_ema_sma_cross_close_filter`

- FMZ source id: 437693 (lineage).
- Source: https://www.fmz.com/strategy/437693 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-04 17:59:04). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C104). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crossing |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [20, 10] x `sma_length` [20, 40]: **4 trials**.

## Ambiguities resolved

- Call-order fills. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
