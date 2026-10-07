# #363797 Backtesting- Indicator -> `fmz_363797_ema_cross_close_trail`

- Source: https://www.fmz.com/strategy/363797 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-17 14:05:42). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | Inactive sizing lines (commented-out strategy() etc.) -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND363797` (Jaccard 0.65-0.80) with #436984 (PORT_CANDIDATE); best Jaccard 0.794 with #436984. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema1` [9, 14] x `ema2` [22, 34] x `stop_loss` [0.02, 0.035] = **8 trials**. EMA 200, trail arm 0.65 % and trail 0.3 % stay at the originals.

## Ambiguities resolved

- Trail and 3.5 % stop are checked on closes: close-based signals (rules 2, 3); mark `trailing_stop_pending`.
- Opening balance / allocation / commission only feed the script's table: not ported.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`trailing_stop_pending`
