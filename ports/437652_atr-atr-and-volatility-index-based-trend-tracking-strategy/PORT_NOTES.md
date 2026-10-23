# #437652 基于ATR和波动性指数的趋势跟踪策略ATR-and-Volatility-Index-Based-Trend-Tracking-Strategy -> `fmz_437652_renko_atr_direction_chop_cross_ema8_reversal`

- FMZ source id: 437652 (lineage).
- Source: https://www.fmz.com/strategy/437652 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-04 15:31:34). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Renko direction with a choppiness breakdown and EMA momentum |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 10 % of equity, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`chop_len` [14, 21] x `box_atr` [14, 28]: **4 trials**; CHOP level 61.8, EMA 8.

## Ambiguities resolved

- Tick exits inside the short block not ported. Volume not used (plot only). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "choppiness"`.

## Marks

`none`
