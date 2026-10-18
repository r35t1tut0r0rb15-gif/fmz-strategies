# #435868 拉盖尔RSI交易策略Laguerre-RSI-Trading-Strategy -> `fmz_435868_laguerre_cu_cd_cross`

- FMZ source id: 435868 (lineage).
- Source: https://www.fmz.com/strategy/435868 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-19 14:04:46). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C82). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Filter momentum |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`alpha` [0.2, 0.4, 0.6]: **3 trials**.

## Ambiguities resolved

- Filter from zero; cu / cd crossings. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "laguerre"`.

## Marks

`none`
