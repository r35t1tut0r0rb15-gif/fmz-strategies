# #362868 Mobo Bands -> `fmz_362868_mobo_band_break`

- Source: https://www.fmz.com/strategy/362868 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-13 14:36:34). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A9). Not run.

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

`dpo_len` [9, 13, 21] x `mobo_len` [10, 20] x `num_dev` [0.8, 1.2] = **12 trials** (symmetric bands, as the defaults).

## Ambiguities resolved

- DPO lag `int(dpo/2 + 1)` = 7 for 13 under either division rule; population stdev.
- Long needs `wasDn[1]` (last band break was down), short needs `wasUp[1]`.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks (2026-10-07)

`none`
