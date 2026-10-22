# #449714 基于WaveTrend指标的趋势追踪策略WaveTrend-Cross-LazyBear-Strategy -> `fmz_449714_wavetrend_10_21_cross_reversal`

- FMZ source id: 449714 (lineage).
- Source: https://www.fmz.com/strategy/449714 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-28 13:56:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C180). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | WaveTrend line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n1` [10, 9] x `n2` [21, 12]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
