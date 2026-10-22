# #474965 Multi Wave Trend Crossing Risk Management Quantitative Strategy -> `fmz_474965_wavetrend_level_recross_bracket_pct_trail_reversal`

- FMZ source id: 474965 (lineage).
- Source: https://www.fmz.com/strategy/474965 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-13 10:51:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C227). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket and a house percent trail |
| 2 | PASS | WaveTrend level re-crossings with a bracket and trail |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [0.002, 0.01] x `activate` [0.03, 0.01]: **4 trials**; levels, stop 50 % and target 5 % fixed.

## Ambiguities resolved

- Trail offset ticks read as 0.2 % of price; armed from the fill. Repeat re-sends not followed. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "wavetrend_oscillator"`.

## Marks

`coarse_bar_stop, trailing_stop, trailing_stop_pending`
