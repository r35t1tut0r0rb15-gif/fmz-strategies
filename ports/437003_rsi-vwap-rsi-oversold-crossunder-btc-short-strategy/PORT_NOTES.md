# #437003 基于RSI指标的跨时间框架策略VWAP-RSI-Oversold-Crossunder-BTC-Short-Strategy -> `fmz_437003_vwap_rsi20_overbought_crossunder_1m_short`

- FMZ source id: 437003 (lineage).
- Source: https://www.fmz.com/strategy/437003 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-29 14:12:54). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | VWAP-RSI overbought crossunder shorts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 50 % of equity, capital 1000, pyramiding 1, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG437003. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 14] x `late_leave` [28, 14]: **4 trials**; levels 85 / 30.

## Ambiguities resolved

- Session VWAP from the broker-day start; late-leave precedence as written. Volume = broker tick volume. Short only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_threshold"`.

## Marks

`none`
