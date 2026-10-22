# #471690 Open Market Exposure Dynamic Position Adjustment Quantitative Trading Strategy -> `fmz_471690_close_vs_prev_open_exposure_threshold_long`

- FMZ source id: 471690 (lineage).
- Source: https://www.fmz.com/strategy/471690 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 14:48:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C209). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close vs previous open thresholds; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`threshold` [0.01, 0.02]: **2 trials**; the per-bar bracket pending.

## Ambiguities resolved

- Cumulative OME = the bar's OME on daily bars; per-bar bracket pending (trailing_stop_pending). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`trailing_stop_pending`
