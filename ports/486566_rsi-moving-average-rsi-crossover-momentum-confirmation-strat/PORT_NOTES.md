# #486566 滑动平均-RSI-交叉动量确认策略-Moving-Average-RSI-Crossover-Momentum-Confirmation-Strategy -> `fmz_486566_sma20_30_cross_rsi_filter_close_tp2pct_long`

- FMZ source id: 486566 (lineage).
- Source: https://www.fmz.com/strategy/486566 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-14 09:35:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C263). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based percent target |
| 2 | PASS | SMA crossings with an RSI filter and a percent target |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_short_period` [20, 10] x `take_profit_perc` [2.0, 4.0]: **4 trials**; SMA 30, RSI 14 / 25 / 75.

## Ambiguities resolved

- The target is tested on closes. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
