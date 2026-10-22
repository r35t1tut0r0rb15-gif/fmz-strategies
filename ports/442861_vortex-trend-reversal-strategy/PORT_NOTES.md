# #442861 Vortex Trend Reversal Strategy -> `fmz_442861_deviation_vs_change_cross_inverted_reversal`

- FMZ source id: 442861 (lineage).
- Source: https://www.fmz.com/strategy/442861 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-26 16:45:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C162). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed deviation vs smoothed change crossings (directions as written) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 30] x `ema_length` [20, 50]: **4 trials**.

## Ambiguities resolved

- Directions inverted as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
