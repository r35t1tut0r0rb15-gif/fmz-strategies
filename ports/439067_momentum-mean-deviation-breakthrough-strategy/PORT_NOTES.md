# #439067 Momentum Mean Deviation Breakthrough Strategy -> `fmz_439067_ergotic_mdi_state`

- FMZ source id: 439067 (lineage).
- Source: https://www.fmz.com/strategy/439067 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-17 14:08:46). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C115). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed mean deviation and its signal |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`r` [32, 64] x `s` [5, 10]: **4 trials**; u 5 fixed.

## Ambiguities resolved

- Level-state entries. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
