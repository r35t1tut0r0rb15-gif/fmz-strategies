# #396182 定投止盈 -> `fmz_396182_red_turn_long_tp`

- Source: https://www.fmz.com/strategy/396182 (PineScript v4, author Zer3192, FMZ last
  modified 2023-01-29 09:49:34). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Target +3 price units -> `tp_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [0.5, 1.0, 2.0] = **3 trials**.

## Ambiguities resolved

- Target +3 price units -> `tp_atr` x ATR(14) at the signal bar (criterion 2), tp_stop shifted one bar.
- Max-loss input unused (no stop), as written. Long only (rule 6).
- No bar size in the source: `FREQ = "bar_size_pending"` (rule 1).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks (2026-10-07)

`bar_size_pending`
