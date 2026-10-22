# #444387 Multiple Exponential Moving Average Trading Strategy -> `fmz_444387_four_ema_stack_turn_long`

- FMZ source id: 444387 (lineage).
- Source: https://www.fmz.com/strategy/444387 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-11 16:17:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C171). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA stack changes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The margin settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_high` [55, 34] x `ema_med` [21, 13]: **4 trials**; the two fastest EMAs fixed.

## Ambiguities resolved

- First bar of the new stack. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
