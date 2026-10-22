# #440110 双移动平均线与Williams平均线组合策略Dual-Moving-Average-and-Williams-Average-Combination-Strategy -> `fmz_440110_ema_2_20_bw_three_lines_combo`

- FMZ source id: 440110 (lineage).
- Source: https://www.fmz.com/strategy/440110 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-26 16:36:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C131). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA band test and displaced averages |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 20] x `l_length` [13, 21]: **4 trials**; the other lengths and offsets fixed.

## Ambiguities resolved

- Start date dropped. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
