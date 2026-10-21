# #438946 Trend Strength Confirm Bars Strategy -> `fmz_438946_confirm_bars_runs`

- FMZ source id: 438946 (lineage).
- Source: https://www.fmz.com/strategy/438946 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-16 15:22:53). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C114). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close runs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND438946. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`confirm_bars` [1, 2, 3, 4]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
