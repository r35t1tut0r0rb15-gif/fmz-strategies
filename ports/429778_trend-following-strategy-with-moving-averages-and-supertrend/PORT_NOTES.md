# #429778 Trend Following Strategy with Moving Averages and SuperTrend -> `fmz_429778_weekly_frama_cross`

- FMZ source id: 429778 (lineage).
- Source: https://www.fmz.com/strategy/429778 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-20 16:50:01). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly values from completed broker weeks. |
| 2 | PASS | A fractal-dimension adaptive average of prices (scale-free alpha). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The off-by-default TP / SL / trail stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [12, 24] x `frama_sc` [200, 100]: **4 trials**; FC 1 and the weekly resolution fixed.

## Ambiguities resolved

- Weekly values = last completed broker week (approximation stated). REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
