# #435133 EMA Tracking Trend Suppressing Oscillation Strategy -> `fmz_435133_ema_tts_stc_bracket`

- FMZ source id: 435133 (lineage).
- Source: https://www.fmz.com/strategy/435133 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-12 15:52:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C74). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar |
| 2 | PASS | Average, trend-line and cycle states with swing exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tt_mult` [3.0, 2.0] x `profit` [0.001, 0.01]: **4 trials**; EMA 200, TT 21 and STC 12 / 26 / 50 fixed.

## Ambiguities resolved

- Signal-bar bracket; flat tracked through it. Mark coarse_bar_stop. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`
