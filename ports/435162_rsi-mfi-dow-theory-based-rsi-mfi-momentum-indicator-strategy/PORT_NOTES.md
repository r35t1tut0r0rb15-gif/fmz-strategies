# #435162 基于道氏理论的RSI-MFI动量指标策略Dow-Theory-based-RSI-MFI-Momentum-Indicator-Strategy -> `fmz_435162_dow_factor_rsi5_volume_correlation_50_cross_reversal`

- FMZ source id: 435162 (lineage).
- Source: https://www.fmz.com/strategy/435162 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-12 17:54:58). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Price-volume-correlation weighted RSI crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, commission 0.125 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [5, 10]: **2 trials**.

## Ambiguities resolved

- Script's own RSI (rma from 0) and EMA-centred correlation. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_threshold"`.

## Marks

`none`
