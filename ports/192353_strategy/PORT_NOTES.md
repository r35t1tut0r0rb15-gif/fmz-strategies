# #192353 海龟 -> `fmz_192353_turtle_55_highest_low_exit`

- Source: https://www.fmz.com/strategy/192353 (Python, author aawww, FMZ last modified
  2020-03-23 14:44:24). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Polls the forming bar; the port evaluates on completed bars. |
| 2 | PASS | Channels in bars, distances in ATR (N). |
| 3 | PASS (screen: REVIEW) | Quarterly futures contract is the venue only. |
| 4 | DONE | Unit formula (1 % of equity per N), 4-unit cap, +/-0.5 % marketable limit prices, position reconciliation -> `original_sizing.txt`. Adds kept only as the stop reference. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`entry_period` [40, 55, 70] x `exit_period` [10, 20, 30] x `stop_atr` [1.5, 2, 3] = **27 trials**.
The code's effective values are 55 and 20 (hard-coded lines override the 20/10 arguments).

## Ambiguities resolved

- **Author slip kept**: the long exit level is `TA.Highest(records, 20, 'Low')` (highest low), not
  the lowest low. Ported as written; this makes long exits much tighter than short exits. A
  corrected variant would be a separate module and was not made (only rule 5 asks for "as meant"
  twins). Flagged in the worker report.
- Hard-coded 55/20 override the arguments; the port's defaults follow the code.
- BOLL and CMI are computed but unused (their uses are commented out).
- No bar size in the source: `FREQ = "bar_size_pending"`, mark `bar_size_pending` (rule 1).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks (2026-10-07)

`bar_size_pending`
