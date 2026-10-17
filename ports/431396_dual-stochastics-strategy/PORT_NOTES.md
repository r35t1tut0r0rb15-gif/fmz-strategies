# #431396 Dual Stochastics Strategy -> `fmz_431396_dual_speed_stochastics`

- FMZ source id: 431396 (lineage).
- Source: https://www.fmz.com/strategy/431396 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-07 15:25:19). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND431396. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [54, 27] x `smooth_k` [12, 6]: **4 trials**; D 3 and the x3 slow factor fixed.

## Ambiguities resolved

- Pending (not emitted as written): the trail_points-only exits. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`trailing_stop_pending`
