# #475624 Dynamic Wave Trend Tracking Strategy -> `fmz_475624_wavetrend_45_cross_sma500_trend_reversal`

- FMZ source id: 475624 (lineage).
- Source: https://www.fmz.com/strategy/475624 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-20 16:17:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C229). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | WaveTrend level crossings with a trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_length` [500, 200] x `level` [45, 60]: **4 trials**; the oversold level is its negative.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "wavetrend_oscillator"`.

## Marks

`none`
