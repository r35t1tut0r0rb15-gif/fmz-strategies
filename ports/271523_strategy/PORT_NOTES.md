# #271523 韭菜保护程序唐安奇通道均仓策略 -> `fmz_271523_weekly_breakout_ma_regime_long`

- Source: https://www.fmz.com/strategy/271523 (Python, author 去者伯仁, FMZ last modified
  2021-07-20 17:27:39). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Weekly regime evaluated each minute on the forming week; the port evaluates on each completed broker day with the week to date. |
| 2 | PASS | Channel and MA on bars only. |
| 3 | PASS | Spot only. |
| 4 | DONE | 100 % / 50 % exposure, the 1 %-step 50/50 rebalancing ladder and its 10x fast steps -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. Same author's #266142 (pure 50/50 rebalancing, rejected) is this strategy's middle state alone. |
| 7 | IGNORED | The description's "avoided the crash" claim is not used. |

## Declared grid (criterion 5)

`hh_weeks` [10, 20, 30] x `ma_weeks` [5, 10, 20] = **9 trials**.

## Ambiguities resolved

- Exposure (all-in vs 50 %) is sizing; in/out is the signal.
- Weeks are calendar weeks of broker days, not the source's 7-record groups anchored at the start
  of FMZ's data window (which shift with the window and do not mean "week" for 5-day markets).
- Warm-up: no signal until 20 completed weeks exist (the source's short-history branch would
  hold 50 %).
- `FREQ = "1D"`: the code reads `PERIOD_D1` records (the header's `1m` is the backtest clock).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`: in while above a weekly MA (with a breakout override).

## Marks (2026-10-07)

`none`
