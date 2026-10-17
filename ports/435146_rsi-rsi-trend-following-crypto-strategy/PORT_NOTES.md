# #435146 RSI趋势追踪型加密货币策略RSI-Trend-Following-Crypto-Strategy -> `fmz_435146_rsi_35_75_cross_long`

- FMZ source id: 435146 (lineage).
- Source: https://www.fmz.com/strategy/435146 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-12 16:26:49). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C74). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI level crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_long` [35, 50] x `rsi_close` [75, 65]: **4 trials**; RSI 14 fixed.

## Ambiguities resolved

- Off-by-default emergency exit not ported. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
