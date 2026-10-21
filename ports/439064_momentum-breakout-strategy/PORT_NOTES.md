# #439064 Momentum Breakout Strategy -> `fmz_439064_momentum_sign_runs`

- FMZ source id: 439064 (lineage).
- Source: https://www.fmz.com/strategy/439064 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-17 13:58:19). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C115). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Momentum sign runs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND438946. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`momentum_length` [14, 28] x `confirm_bars` [1, 3]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
