# #441157 RSI指标跨周期交叉的止盈止损策略RSI-Indicator-Cross-Cycle-Profit-and-Stop-Loss-Strategy -> `fmz_441157_rsi4_dip_at_high_weekly_trend_atr_exits_long`

- FMZ source id: 441157 (lineage).
- Source: https://www.fmz.com/strategy/441157 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-06 11:43:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C147). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly values from completed weeks |
| 2 | PASS | High check, RSI cross and ATR distance tests |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_period` [4, 2] x `rsi_thresh` [30, 20]: **4 trials**; the highs, weekly length and ATR multiples fixed.

## Ambiguities resolved

- Weekly average from completed weeks of the 2-day blocks; close[1] exits against the fill. Long only. FREQ = "2D".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
