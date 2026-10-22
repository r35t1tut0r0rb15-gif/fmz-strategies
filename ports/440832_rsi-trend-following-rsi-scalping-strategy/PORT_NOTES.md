# #440832 基于RSI的追踪趋势策略Trend-Following-RSI-Scalping-Strategy -> `fmz_440832_rsi70_momentum_long_close_target`

- FMZ source id: 440832 (lineage).
- Source: https://www.fmz.com/strategy/440832 (PineScript v1, author ChaoZhang, FMZ last
  modified 2024-02-02 14:54:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C140). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested target |
| 2 | PASS | RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent of equity, capital and commission settings. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`take_profit` [6, 3] x `exit_rsi` [55, 50]: **4 trials**; entry 70 and RSI 14 fixed.

## Ambiguities resolved

- Close-tested target. Long only. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
