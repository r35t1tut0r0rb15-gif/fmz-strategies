# #427684 Three Line Breakout Strategy -> `fmz_427684_hpotter_three_line_break`

- FMZ source id: 427684 (lineage).
- Source: https://www.fmz.com/strategy/427684 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-23 16:02:20). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C11) AS WRITTEN. Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Closes only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders ("Trade reverse" fixed off): **1 trial**, the source as written.

## Ambiguities resolved

- The line variables are not `var`: on a bar without a new line they reset to the close, as written.
- xtrend[1] is na on the first bar (down-trend branch). REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## Decision owed

Intended version: lines kept between new lines (the classic three-line break).

## FAMILY (proposed, user to confirm)

`FAMILY = "price_action_breakout"`.

## Marks

`none`
