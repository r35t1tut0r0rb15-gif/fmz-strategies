# #490517 多重确认变动平均趋势与随机RSI动量交易策略-Multi-Confirmation-EMA-Trend-and-Stochastic-RSI-Momentum-Trading-Strategy -> `fmz_490517_ema_11_50_cross_stoch_rsi_long`

- FMZ source id: 490517 (lineage).
- Source: https://www.fmz.com/strategy/490517 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-14 11:25:18). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMAs and an oscillator |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [11, 20] x `slow` [50, 100]: **4 trials**; defaults 11 / 50 (the source's); stochastic RSI 10 / 10, %K 15,
%D 7 fixed.

## Ambiguities resolved

- Stochastic of the RSI with windows including the current bar; na on a zero range. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
