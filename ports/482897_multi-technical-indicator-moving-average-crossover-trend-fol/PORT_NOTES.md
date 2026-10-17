# #482897 多重技术指标均线交叉趋势跟踪量化交易策略-Multi-Technical-Indicator-Moving-Average-Crossover-Trend-Following-Quantitative-Trading-Strategy -> `fmz_482897_bb_reentry_rsi_macd_stoch_reversal`

- FMZ source id: 482897 (lineage).
- Source: https://www.fmz.com/strategy/482897 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 16:56:38). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI, MACD, a stochastic and Bollinger bands. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The lot size quoted, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_os` [30, 40] x `stoch_os` [20, 30]: **4 trials**; defaults 30 / 20 (the source's; the short side uses 100 minus
each, 70 / 80 as written); RSI 14, BB 20 x 2, MACD 12 / 26 / 9 and stochastic 14 fixed.

## Ambiguities resolved

- The conditions are as written (rare). `ta.bb` uses the population standard deviation.
- REVERSAL INTENDED; no exits or stops. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
