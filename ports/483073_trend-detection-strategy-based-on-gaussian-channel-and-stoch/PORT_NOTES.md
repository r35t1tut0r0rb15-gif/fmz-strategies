# #483073 基于高斯通道与随机相对强弱指数过滤的趋势判断策略-Trend-Detection-Strategy-Based-on-Gaussian-Channel-and-Stochastic-RSI-Filter -> `fmz_483073_gaussian_channel_stoch_reentry`

- FMZ source id: 483073 (lineage).
- Source: https://www.fmz.com/strategy/483073 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 11:42:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A recursive filter channel in percent and a stochastic. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 50] x `mult` [2.0, 1.0]: **4 trials**; defaults 100 / 2 (the source's); stochastic 14 / 3 / 3
(80 / 20) fixed.

## Ambiguities resolved

- The "Stochastic RSI" is `ta.stoch` of price, as written.
- Closes act on the position held at the bar's start and never undo an entry on that bar (as #430850); the later short
  entry wins over a long on one bar. Target-position state machine.
- Clock (C6): no position before 2023-01-01 00:00 UTC (the source's `close_all` window; Pine would open and close
  one-bar trades there).
- REVERSAL INTENDED. No stops. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
