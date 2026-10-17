# #432215 基于CT-TTM指标的量化交易策略CT-TTM-Squeeze-Based-Quantitative-Trading-Strategy -> `fmz_432215_ttm_momentum_sign`

- FMZ source id: 432215 (lineage).
- Source: https://www.fmz.com/strategy/432215 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-15 16:06:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C50). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | The sign of a detrended regression |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10, 40]: **3 trials**.

## Ambiguities resolved

- The squeeze colour is display only. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_squeeze"`.

## Marks

`none`
