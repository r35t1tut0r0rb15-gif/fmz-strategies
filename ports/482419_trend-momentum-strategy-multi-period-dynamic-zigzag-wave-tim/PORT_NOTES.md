# #482419 Trend Momentum Strategy Multi Period Dynamic ZigZag Wave Timing System -> `fmz_482419_zigzag5_dev1_williams_r_cross_pct_bracket_reversal`

- FMZ source id: 482419 (lineage).
- Source: https://www.fmz.com/strategy/482419 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 13:29:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C243). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Zigzag direction with Williams %R re-entries and a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 300 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`depth` [5, 10] x `deviation` [1.0, 3.0]: **4 trials**; Williams %R 14 / -20 / -80, stop 1 %, target 2 %.

## Ambiguities resolved

- Repeat-signal re-sends not followed. REVERSAL INTENDED. FREQ = "2D" (two broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "support_resistance"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
