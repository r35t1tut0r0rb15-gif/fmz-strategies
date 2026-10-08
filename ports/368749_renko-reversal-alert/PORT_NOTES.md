# #368749 Renko Reversal alert -> `fmz_368749_bar_reversal_pattern`

- Source: https://www.fmz.com/strategy/368749 (PineScript v4, author Zer3192, FMZ last
  modified 2022-06-12 18:32:42). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A16). Not run.

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

No parameters: **1 trial**, the source as written.

## Ambiguities resolved

- Meant for Renko charts; run on the header's 4 h time bars, as the FMZ backtest does.
- Pattern fixed in the source.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks (2026-10-07)

`none`
