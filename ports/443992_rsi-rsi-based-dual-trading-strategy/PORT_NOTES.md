# #443992 基于RSI指标的双向交易策略RSI-based-Dual-Trading-Strategy -> `fmz_443992_rsi14_30_70_cross_long`

- FMZ source id: 443992 (lineage).
- Source: https://www.fmz.com/strategy/443992 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-08 14:28:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C168). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI level crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `buy_level` [30, 20]: **4 trials** (sell level = 100 - buy level).

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
