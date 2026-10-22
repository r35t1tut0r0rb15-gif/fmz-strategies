# #440800 Single Point Moving Average Breakout Strategy -> `fmz_440800_chande_momentum_extreme_cross`

- FMZ source id: 440800 (lineage).
- Source: https://www.fmz.com/strategy/440800 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-02 11:19:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C140). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Chande Momentum crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [9, 20] x `buyline` [-80, -50]: **4 trials**; sell line = -buy line.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
