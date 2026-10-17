# #434968 随机超买超卖区间RSI策略Stochastic-Oversold-and-Overbought-Range-RSI-Strategy -> `fmz_434968_rsi6_multi_level_long`

- FMZ source id: 434968 (lineage).
- Source: https://www.fmz.com/strategy/434968 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-11 13:19:08). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C71). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI level crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [6, 14]: **2 trials**; the level sets fixed.

## Ambiguities resolved

- Cancel has no effect with bar-close orders. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
