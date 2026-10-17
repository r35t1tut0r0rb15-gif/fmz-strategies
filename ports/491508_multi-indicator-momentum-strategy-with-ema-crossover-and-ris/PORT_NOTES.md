# #491508 均线交叉与多指标动量风险控制策略-Multi-Indicator-Momentum-Strategy-with-EMA-Crossover-and-Risk-Management -> `fmz_491508_ema_cross_rsi_macd_bracket`

- FMZ source id: 491508 (lineage).
- Source: https://www.fmz.com/strategy/491508 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-21 16:00:38). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | PASS | EMAs, oscillators and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [1.0, 2.0] x `tp_pct` [2.0, 4.0]: **4 trials**; defaults 1 / 2 (the source's); EMA 9 / 21, RSI 14 and MACD
12 / 26 / 9 fixed.

## Ambiguities resolved

- The bracket is placed on the signal bar; re-based on the fill (house rule).
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D"; stops on daily bars: `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
