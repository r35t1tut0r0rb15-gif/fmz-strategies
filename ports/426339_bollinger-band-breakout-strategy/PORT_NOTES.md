# #426339 Bollinger Band Breakout strategy -> `fmz_426339_bollinger_breakout_long`

- Source: https://www.fmz.com/strategy/426339 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-11 12:24:43). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND426339` (Jaccard 0.65-0.80) with #437565 (PORT_CANDIDATE); best Jaccard 0.661 with #437565. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `mult` [1.5, 2.0]: **4 trials**, defaults 20 / 1.5 (the source's; its comment pairs 10 with 2.0).

## Ambiguities resolved

- Long only: the source has no short entry.
- Pine population stdev.
- Daily bars are broker days.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks (2026-10-07)

`none`
