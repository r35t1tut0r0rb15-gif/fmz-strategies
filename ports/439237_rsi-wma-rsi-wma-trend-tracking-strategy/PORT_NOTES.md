# #439237 基于RSI和WMA的趋势追踪策略RSI-WMA-Trend-Tracking-Strategy -> `fmz_439237_wma_rsi2_dip_wma50_exit_long`

- FMZ source id: 439237 (lineage).
- Source: https://www.fmz.com/strategy/439237 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-18 15:35:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C118). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI and WMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [2, 3] x `wma_length` [50, 100]: **4 trials**; oversold 10 fixed.

## Ambiguities resolved

- Long only. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
