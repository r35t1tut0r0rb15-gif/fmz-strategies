# #362916 Crodls Supertrend -> `fmz_362916_triple_supertrend_ema200_volume_flow_stoch_turn_reversal`

- FMZ source id: 362916 (lineage).
- Source: https://www.fmz.com/strategy/362916 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-13 17:43:21). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend agreement with trend, volume-flow and stochastic filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [200, 100] x `flow_len` [13, 26]: **4 trials**; SuperTrends 3 / 12, 2 / 11, 1 / 10, Stoch 14 / 1 / 3.

## Ambiguities resolved

- Operator precedence as written. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
