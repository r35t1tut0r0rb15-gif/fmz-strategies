# #446441 ADR均线交叉策略-融合多维度技术指标和严格止盈止损的交易方法EMA-Cross-ADR-Strategy-A-Multidimensional-Technical-Indicator-Based-Trading-Method-with-Strict-Risk-Management -> `fmz_446441_ema10_50_cross_adr_floor_avg_swing_bracket_reversal`

- FMZ source id: 446441 (lineage).
- Source: https://www.fmz.com/strategy/446441 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-28 16:46:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C174). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed on the signal bar (re-sent levels marked) |
| 2 | PASS | EMA crossings with a range floor, swing-average bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [2.0, 1.5] x `lookback` [10, 20]: **4 trials**; the EMAs and the ADR floor fixed.

## Ambiguities resolved

- ADR floor as 0.000238 of the close; levels from the signal bar; break-even never acts. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
