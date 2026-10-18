# #435703 基于均线和RSI的单边多头策略SMA-and-RSI-Long-Only-Strategy -> `fmz_435703_sma_rsi_long_only`

- FMZ source id: 435703 (lineage).
- Source: https://www.fmz.com/strategy/435703 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-18 10:28:10). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C80). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average and RSI rules |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`emapl` [14, 20] x `rsi_period` [14, 7]: **4 trials**; the fast SMA 14, the stop SMA 7 and the RSI levels fixed.

## Ambiguities resolved

- Entry plus an exit on one bar: flat. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
