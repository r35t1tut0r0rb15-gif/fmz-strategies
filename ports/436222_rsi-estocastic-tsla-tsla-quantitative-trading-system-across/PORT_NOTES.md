# #436222 基于RSI和Estocastic指标的TSLA交易策略TSLA-Quantitative-Trading-System-Across-Multiple-Timeframes -> `fmz_436222_rsi_pair_oversold_long_stoch_exit`

- FMZ source id: 436222 (lineage).
- Source: https://www.fmz.com/strategy/436222 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-22 12:50:55). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C87). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI and stochastic levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_fast` [5, 3] x `stoch_exit` [78, 70]: **4 trials**; RSI 14 and the 30 levels fixed.

## Ambiguities resolved

- Second RSI on the chart's close; the 3 % comparison never true, not ported. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
