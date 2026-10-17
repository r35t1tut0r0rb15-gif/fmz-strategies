# #488010 多指数均线交叉动量预警交易策略-Multi-EMA-Crossover-Momentum-Alert-Trading-Strategy -> `fmz_488010_ema_trend_warning_cooldown`

- FMZ source id: 488010 (lineage).
- Source: https://www.fmz.com/strategy/488010 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-24 13:49:59). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMAs and relative gaps. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cooldown` [2, 4] x `exit_len` [15, 20]: **4 trials**; defaults 2 / 15 (the source's); EMA 5 / 10 / 20 / 50 and the
2.5 warning multiple fixed.

## Ambiguities resolved

- The script's `positionState` gates entries (only from flat) and closes, so it tracks the position; closes are
  close-based exit signals. The cooldown counter starts at 0 on a close and adds 1 at the end of each bar (entries
  from the second bar after the close). Opposite entries cannot occur. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_filter"`.

## Marks

`none`
