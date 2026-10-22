# #482427 Adaptive Multi Period Trading Strategy Based on Wave Trend Momentum Breakout -> `fmz_482427_wavetrend10_21_outer_level_cross_reversal`

- FMZ source id: 482427 (lineage).
- Source: https://www.fmz.com/strategy/482427 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 13:52:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C243). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | WaveTrend crossings at the outer levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`level` [60, 53] x `n2` [21, 34]: **4 trials**; channel 10.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "wavetrend"`.

## Marks

`none`
