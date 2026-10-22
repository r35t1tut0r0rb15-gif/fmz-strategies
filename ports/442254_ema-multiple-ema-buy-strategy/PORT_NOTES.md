# #442254 基于多EMA买入策略Multiple-EMA-Buy-Strategy -> `fmz_442254_six_ema_stack_ema200_exit_long`

- FMZ source id: 442254 (lineage).
- Source: https://www.fmz.com/strategy/442254 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-20 15:38:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C153). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stacked EMAs and the EMA 200 exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slowest` [200, 150]: **2 trials**; the other EMAs fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
