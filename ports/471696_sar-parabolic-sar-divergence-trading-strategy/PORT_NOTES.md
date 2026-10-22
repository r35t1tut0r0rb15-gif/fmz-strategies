# #471696 抛物线SAR指标背离交易策略-Parabolic-SAR-Divergence-Trading-Strategy -> `fmz_471696_close_vs_sar_divergence_lag5_reversal`

- FMZ source id: 471696 (lineage).
- Source: https://www.fmz.com/strategy/471696 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 15:12:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C210). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close / SAR direction disagreements |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sar_start` [14.0, 0.02] x `lookback` [5, 1]: **4 trials**; the increment and maximum fixed.

## Ambiguities resolved

- SAR start 14 (the "length" input, as written). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`none`
