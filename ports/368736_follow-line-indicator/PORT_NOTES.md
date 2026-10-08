# #368736 Follow Line Indicator -> `fmz_368736_follow_line_flip`

- Source: https://www.fmz.com/strategy/368736 (PineScript v4, author Zer3192, FMZ last
  modified 2022-06-12 17:01:09). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND368736` (Jaccard 0.65-0.80) with #439855 (PORT_CANDIDATE); best Jaccard 0.781 with #439855. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_period` [14, 21, 34] x `bb_dev` [1.0, 1.5] x `atr_period` [5, 10] = **12 trials**.

## Ambiguities resolved

- Comparisons with an na history are false (first bars keep their value).
- ATR filter default on; same family as #362256.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks (2026-10-07)

`none`
