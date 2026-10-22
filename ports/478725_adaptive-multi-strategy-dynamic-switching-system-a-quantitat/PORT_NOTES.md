# #478725 Adaptive Multi Strategy Dynamic Switching System A Quantitative Trading Strategy Combining Trend Following and Range Oscillation -> `fmz_478725_sma50_trend_band_sma20_cross_pct_bracket_reversal`

- FMZ source id: 478725 (lineage).
- Source: https://www.fmz.com/strategy/478725 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-17 16:02:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C240). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | SMA trend states and crossings with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`band` [0.02, 0.05] x `tp_trend` [0.06, 0.10]: **4 trials**; SMA 50 / 20, stop 2 %, range target 4 %.

## Ambiguities resolved

- Range-bound entries need close == SMA 50 and almost never fire. Repeat-signal re-sends not followed.
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
