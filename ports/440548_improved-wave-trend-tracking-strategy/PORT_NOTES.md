# #440548 Improved Wave Trend Tracking Strategy -> `fmz_440548_wavetrend_level_cross_bar_tests`

- FMZ source id: 440548 (lineage).
- Source: https://www.fmz.com/strategy/440548 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-31 15:35:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C136). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bar-tested target and stop |
| 2 | PASS | WaveTrend level crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [1.0, 2.0] x `sl_pct` [0.5, 1.0]: **4 trials**; WaveTrend 10 / 21 and the levels fixed.

## Ambiguities resolved

- Bar-tested target / stop sent at the next open. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "wavetrend_oscillator"`.

## Marks

`none`
