# #426901 Ichimoku Cloud Market Analysis Strategy -> `fmz_426901_easymoku`

- Source: https://www.fmz.com/strategy/426901 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-01 14:58:48). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`multiplier` [1.0, 3.0, 5.9]: **3 trials**, default 5.9 (the source's; periods 41 / 130 / 260, displacement 130).

## Ambiguities resolved

- KUMO / CHIKOU / TK declared var bool but assigned 1 / 0 / na / -1: numeric reading used (decision owed).
- Fills in issue order; a reversing entry stands.
- FREQ = "5min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks (2026-10-07)

`none`
