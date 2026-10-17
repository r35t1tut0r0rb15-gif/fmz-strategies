# #431960 Extreme Distribution Swing Strategy -> `fmz_431960_cmo_percentile_extremes`

- FMZ source id: 431960 (lineage).
- Source: https://www.fmz.com/strategy/431960 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-13 17:03:08). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C48). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Rolling percentiles of a momentum oscillator |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [9, 20] x `pct` [1, 5]: **4 trials**; the short percentile = 100 - pct; look-back 425 fixed.

## Ambiguities resolved

- Nearest-rank percentiles including the current bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
