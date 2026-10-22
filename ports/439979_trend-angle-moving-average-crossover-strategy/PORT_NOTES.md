# #439979 Trend Angle Moving Average Crossover Strategy -> `fmz_439979_ema56_slope_angle_roc_gate`

- FMZ source id: 439979 (lineage).
- Source: https://www.fmz.com/strategy/439979 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-25 14:35:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C128). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent stop from the fill |
| 2 | PASS | EMA slope angle and ROC gate |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [56, 30] x `pcnt_change` [2, 4]: **4 trials**; ROC 12 and the 2 % stop fixed.

## Ambiguities resolved

- Stop from the fill; the 900 % target dropped. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`coarse_bar_stop`
