# #439854 双向交叉零轴Qstick指标回测策略Bi-directional-Crossing-Zero-Axis-Qstick-Indicator-Backtest-Strategy -> `fmz_439854_hpotter_qstick_zero_state`

- FMZ source id: 439854 (lineage).
- Source: https://www.fmz.com/strategy/439854 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-24 14:14:07). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C125). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average candle body sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 30, 7]: **3 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
