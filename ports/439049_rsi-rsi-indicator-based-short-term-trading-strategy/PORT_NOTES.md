# #439049 基于RSI指标的短线交易策略RSI-Indicator-Based-Short-term-Trading-Strategy -> `fmz_439049_rsi_30_70_cross_long`

- FMZ source id: 439049 (lineage).
- Source: https://www.fmz.com/strategy/439049 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-17 11:49:15). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C115). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI level crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital / close quantity and the entry-price inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `over_sold` [30, 20]: **4 trials**; overbought 70 fixed.

## Ambiguities resolved

- Order prices are entries, not exits; adds not held. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
