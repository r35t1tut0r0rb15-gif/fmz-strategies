# #490517 多重确认变动平均趋势与随机RSI动量交易策略-Multi-Confirmation-EMA-Trend-and-Stochastic-RSI-Momentum-Trading-Strategy -> `fmz_490517_ema11_50_cross_stochrsi_side_long`

- FMZ source id: 490517 (lineage).
- Source: https://www.fmz.com/strategy/490517 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-14 11:25:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C273). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with a stochastic-RSI side filter |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fastLength` [11, 20] x `slowLength` [50, 100]: **4 trials**; Stoch RSI 10 / 15 / 7.

## Ambiguities resolved

- Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
