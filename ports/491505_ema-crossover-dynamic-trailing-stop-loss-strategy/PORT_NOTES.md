# #491505 指数移动平均线交叉动态跟踪止损策略-EMA-Crossover-Dynamic-Trailing-Stop-Loss-Strategy -> `fmz_491505_ema_9_21_cross_close_trail`

- FMZ source id: 491505 (lineage).
- Source: https://www.fmz.com/strategy/491505 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-21 15:53:17). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a close-checked trail. |
| 2 | PASS | EMAs and a percentage. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [1.0, 3.0] x `ema_long` [21, 50]: **4 trials**; defaults 1 / 21 (the source's); EMA 9 fixed.

## Ambiguities resolved

- The 1 % trail is checked on closes: a close-based exit signal (rule 2), no mark. The reference close starts at
  the signal bar's close.
- Source order: resets, trail checks on the held position, entries. REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
