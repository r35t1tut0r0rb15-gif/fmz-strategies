# #439098 布林带穿越均值PB指标策略Bandpass-Mean-PB-Indicator-Strategy -> `fmz_439098_super_passband_rms_cross`

- FMZ source id: 439098 (lineage).
- Source: https://www.fmz.com/strategy/439098 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-17 17:10:53). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C116). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Passband filter and RMS crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period1` [41, 20] x `period2` [54, 40]: **4 trials**.

## Ambiguities resolved

- RMS divides a 50-value sum by 40 as written. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
