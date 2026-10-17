# #432898 Trend Following Strategy Based on Trend Confidence -> `fmz_432898_trend_confidence_cross`

- FMZ source id: 432898 (lineage).
- Source: https://www.fmz.com/strategy/432898 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-22 15:50:07). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C55). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A scale-free slope-to-noise ratio |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the stop orders quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [30, 15] x `long_entry` [0.25, 0.5]: **4 trials**; the other thresholds fixed.

## Ambiguities resolved

- Stop orders without a level as written (intent owed). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "slope_momentum"`.

## Marks

`none`
