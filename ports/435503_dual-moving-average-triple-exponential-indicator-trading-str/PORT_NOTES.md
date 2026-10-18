# #435503 Dual Moving Average Triple Exponential Indicator Trading Strategy -> `fmz_435503_stoch_rsi_ema_stack`

- FMZ source id: 435503 (lineage).
- Source: https://www.fmz.com/strategy/435503 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-15 15:39:45). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C79). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic RSI and EMA stack |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_rsi` [28, 14] x `lo_level` [23, 30]: **4 trials**; the upper level is 100 minus the lower; K 6, D 6 and the EMA stack fixed.

## Ambiguities resolved

- Crossed close names as written; sequential order fills. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
