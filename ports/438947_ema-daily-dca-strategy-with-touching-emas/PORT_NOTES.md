# #438947 每日均成本策略结合EMA触碰信号Daily-DCA-Strategy-with-Touching-EMAs -> `fmz_438947_day_start_ema_cross_one_bar`

- FMZ source id: 438947 (lineage).
- Source: https://www.fmz.com/strategy/438947 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-16 15:30:17). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C114). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Day-start EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The daily investment quantity and pyramiding stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fastest` [5, 3] x `slowest` [200, 100]: **4 trials**; the middle EMAs 10 / 20 / 50 / 100 fixed.

## Ambiguities resolved

- Always-true sell: one-bar trades; start date always true. Long only. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`
