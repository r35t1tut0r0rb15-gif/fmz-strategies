# #482786 高斯通道趋势跟踪与随机相对强弱指标交易策略-Gaussian-Channel-Trend-Following-with-Stochastic-RSI-Trading-Strategy -> `fmz_482786_gaussian_channel_break_stoch_rsi_long`

- FMZ source id: 482786 (lineage).
- Source: https://www.fmz.com/strategy/482786 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 11:01:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A weighted channel and a stochastic RSI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity; the commission is a cost. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 30] x `multiplier` [2.0, 1.5]: **4 trials**; defaults 20 / 2 (the source's); RSI 14 and the
stochastic 14 / 3 / 3 fixed.

## Ambiguities resolved

- The Gaussian weights cover lags 0 to length - 1 (no future bars); the deviation is the same-weighted one.
- Clock rule (check 9 / C6): the 2018-01-01 to 2069-01-01 range is read as UTC; nothing trades before 2018.
- Long only. Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

none
