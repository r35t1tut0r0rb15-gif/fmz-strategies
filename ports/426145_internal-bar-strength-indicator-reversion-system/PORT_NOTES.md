# #426145 Internal Bar Strength Indicator Reversion system -> `fmz_426145_ibs_extreme_bracket`

- Source: https://www.fmz.com/strategy/426145 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-08 16:33:39). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Profit 10 / loss 2 ticks -> ATR(14) multiples. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ibs_low` [5, 10] x `ibs_high` [95, 99] x `sl_atr` [0.25, 0.5, 1.0] (target = 5 x stop) = **12 trials**.

## Ambiguities resolved

- Profit 10 / loss 2 ticks -> 5 `sl_atr` / `sl_atr` x ATR(14) at the signal bar (criterion 2).
- Entries reverse; repeated entries while in position are ignored.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks (2026-10-07)

`none`
