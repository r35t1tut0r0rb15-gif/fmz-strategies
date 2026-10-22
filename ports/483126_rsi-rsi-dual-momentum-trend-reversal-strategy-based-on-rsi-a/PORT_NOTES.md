# #483126 基于RSI和随机RSI的双重动量趋势反转策略-Dual-Momentum-Trend-Reversal-Strategy-Based-on-RSI-and-Stochastic-RSI -> `fmz_483126_rsi14_extreme_stochrsi_kd_cross_reversal`

- FMZ source id: 483126 (lineage).
- Source: https://www.fmz.com/strategy/483126 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:53:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C258). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI extremes with Stochastic RSI crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `stoch_length` [14, 9]: **4 trials**; K 3, D 3, levels 30 / 70 and 20 / 80.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
