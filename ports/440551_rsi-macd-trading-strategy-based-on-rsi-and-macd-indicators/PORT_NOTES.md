# #440551 基于RSI和MACD指标的交易策略Trading-Strategy-Based-on-RSI-and-MACD-Indicators -> `fmz_440551_rsi_cross_deep_macd_stop`

- FMZ source id: 440551 (lineage).
- Source: https://www.fmz.com/strategy/440551 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-31 16:07:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C137). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | ADAPT | Price-unit MACD levels -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.025, 0.05] x `rsi_period` [14, 7]: **4 trials**; MACD fractions fixed.

## Ambiguities resolved

- MACD levels as fractions of the close. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`
