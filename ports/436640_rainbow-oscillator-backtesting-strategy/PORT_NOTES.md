# #436640 Rainbow Oscillator Backtesting Strategy -> `fmz_436640_rainbow_oscillator_state`

- FMZ source id: 436640 (lineage).
- Source: https://www.fmz.com/strategy/436640 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-26 15:08:17). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C94). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator sign state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [2, 3] x `length_hhll` [10, 20]: **4 trials**; the reverse switch (off) fixed.

## Ambiguities resolved

- State entries sent on every bar of the state. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
