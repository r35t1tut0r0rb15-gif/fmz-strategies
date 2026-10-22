# #458041 Darvas-Box-Breakout-and-Risk-Management-Strategy-Darvas-盒子突破与风险管理策略 -> `fmz_458041_darvas_box_breakout_long`

- FMZ source id: 458041 (lineage).
- Source: https://www.fmz.com/strategy/458041 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 14:22:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C199). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Darvas box breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity sizing stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`boxp` [5, 8]: **2 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
