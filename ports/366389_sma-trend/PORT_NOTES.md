# #366389 SMA Trend -> `fmz_366389_sma_swing_trend`

- Source: https://www.fmz.com/strategy/366389 (PineScript v4, author Zer3192, FMZ last
  modified 2022-06-05 06:51:08). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Offset log(10) (price units) -> `off_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len_c` [10, 20, 40] x `factor` [0.02, 0.05] x `off_atr` [0.0, 0.25] = **12 trials**.

## Ambiguities resolved

- The +- log(10) price-unit offset -> +- `off_atr` x ATR(14) (criterion 2); 0 drops it.
- buy/sell equal the trend flips (flips alternate). Swing machine with Pine nz() semantics.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
