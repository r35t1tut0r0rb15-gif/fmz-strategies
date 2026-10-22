# #454341 Fisher变换动态阈值趋势跟踪策略-Fisher-Transform-Dynamic-Threshold-Trend-Following-Strategy -> `fmz_454341_fisher_turn_beyond_threshold_reversal`

- FMZ source id: 454341 (lineage).
- Source: https://www.fmz.com/strategy/454341 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-17 15:01:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C194). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Fisher transform turns at extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `threshold` [2.6, 1.5]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
