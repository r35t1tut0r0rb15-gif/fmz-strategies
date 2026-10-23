# #428787 Four Exponential Moving Averages and Volume Strategy -> `fmz_428787_four_ema_stack_ease_of_movement_long`

- FMZ source id: 428787 (lineage).
- Source: https://www.fmz.com/strategy/428787 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-09 15:05:47). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA stack order with an ease-of-movement filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, capital 1000, commission 0.1 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema4l` [180, 100] x `length` [14, 28]: **4 trials**; EMA 13 / 21 / 50.

## Ambiguities resolved

- option1 only. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_stack"`.

## Marks

`none`
