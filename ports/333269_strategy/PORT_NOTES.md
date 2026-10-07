# #333269 数字货币期货双均线拐点策略教学 -> `fmz_333269_dual_ema_turning_point`

- Source: https://www.fmz.com/strategy/333269 (JavaScript, author 发明者量化-小小梦, FMZ last
  modified 2025-02-18 17:34:56). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Turning points use completed bars only. |
| 2 | ADAPT | Price-unit `profitTarget` -> `tp_atr` x ATR(14). |
| 3 | PASS (screen: PASS) | Contract type is an argument (venue only). |
| 4 | DONE | Fixed `amount`, cancel-all and cover helpers -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`ema1` [5, 10, 20] x `ema2` [20, 40, 60] x `tp_atr` [1, 2, 4] = **27 trials**.

## Ambiguities resolved

- **No numeric defaults in the source** (the argument table's default column holds
  descriptions). Defaults 10 / 40 / 2 ATR are declared here; the grid brackets them.
- The take-profit is checked on completed bars (the source checks the live price); after a
  take-profit the next entry needs a new turning point (the source could re-enter at once if
  the last completed bars still show one).
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
