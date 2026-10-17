# #483525 基于动量增强型简单移动平均线和RSI的趋势跟踪策略-Momentum-Enhanced-Simple-Moving-Average-and-RSI-Strategy-for-Trend-Following -> `fmz_483525_sma8_21_cross_rsi_pct_bracket`

- FMZ source id: 483525 (lineage).
- Source: https://www.fmz.com/strategy/483525 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-24 10:19:03). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; a fixed bracket from the fill. |
| 2 | PASS | Moving averages, RSI and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [1.0, 1.5] x `tp_pct` [2.0, 3.0]: **4 trials**; defaults 1 / 2 (the source's); SMA 8 / 21, RSI 14 and the
70 / 30 filters fixed.

## Ambiguities resolved

- The exits use `strategy.position_avg_price` (the fill) on every bar: a fixed bracket from the fill. Pine arms it
  only at the fill bar's close (na on the signal bar); the house bracket is live from the fill.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "6min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
