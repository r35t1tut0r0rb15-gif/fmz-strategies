# #436619 动量震荡Stochastic-RSI交易策略Stochastic-RSI-Momentum-Oscillation-Trading-Strategy -> `fmz_436619_stoch_rsi_cross_trend_long`

- FMZ source id: 436619 (lineage).
- Source: https://www.fmz.com/strategy/436619 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-26 12:11:21). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C93). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | REVIEW | Stochastic RSI crossing with a trend filter and a delayed exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The gamble sizing and the quantity formula stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.10, 0.05] x `tp_pct` [0.08, 0.04]: **4 trials**; the oscillator settings and the delay fixed.

## Ambiguities resolved

- Short side off by default, not ported; start date treated as open; gamble sizing is sizing. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
