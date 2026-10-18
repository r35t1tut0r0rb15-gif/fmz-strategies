# #436644 Inertia Indicator Trading Strategy -> `fmz_436644_inertia_rvi_state`

- FMZ source id: 436644 (lineage).
- Source: https://www.fmz.com/strategy/436644 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-26 15:42:33). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C94). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volatility index state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427893. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [10, 20] x `smooth` [14, 7]: **4 trials**; the reverse switch (off) fixed.

## Ambiguities resolved

- State entries sent on every bar of the state. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
