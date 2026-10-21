# #436793 Trend Breakout Strategy -> `fmz_436793_range_vs_average_state`

- FMZ source id: 436793 (lineage).
- Source: https://www.fmz.com/strategy/436793 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-27 17:34:31). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C96). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Range against its own average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [16, 30] x `bars_back` [1, 2]: **4 trials**; reverse off.

## Ambiguities resolved

- State entries sent on every bar of the state. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_regime"`.

## Marks

`none`
