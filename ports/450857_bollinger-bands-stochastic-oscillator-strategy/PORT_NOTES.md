# #450857 Bollinger-Bands-Stochastic-Oscillator-Strategy-布林带随机振荡器策略 -> `fmz_450857_bb34_two_sd_breakout_reversal`

- FMZ source id: 450857 (lineage).
- Source: https://www.fmz.com/strategy/450857 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-09 15:59:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C183). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [34, 20] x `mult` [2.0, 1.5]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
