# #489646 双指数移动平均交叉转向退出策略-Dual-EMA-Cross-with-Directional-Exit-Strategy -> `fmz_489646_ema_5_21_cross_always_in`

- FMZ source id: 489646 (lineage).
- Source: https://www.fmz.com/strategy/489646 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-07 12:00:24). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMAs only |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 10] x `slow` [21, 50]: **4 trials**; defaults 5 / 21 (the source's).

## Ambiguities resolved

- No "turning" exit exists in the code; reversals only. REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
