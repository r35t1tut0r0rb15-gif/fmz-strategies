# #448778 MACD-Crossover-Strategy-MACD-交叉策略 -> `fmz_448778_cdc_action_zone_transition_long`

- FMZ source id: 448778 (lineage).
- Source: https://www.fmz.com/strategy/448778 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-18 17:56:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C178). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA action-zone transitions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 9] x `slow` [26, 21]: **4 trials**; the smoothing 1 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
