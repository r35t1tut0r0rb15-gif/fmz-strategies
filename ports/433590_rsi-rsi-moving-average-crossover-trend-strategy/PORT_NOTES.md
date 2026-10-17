# #433590 RSI均线交叉趋势策略RSI-Moving-Average-Crossover-Trend-Strategy -> `fmz_433590_rsi_ema_sma_long`

- FMZ source id: 433590 (lineage).
- Source: https://www.fmz.com/strategy/433590 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-28 17:03:56). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C62). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI averages and a price EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [16, 8] x `price_ema` [8, 21]: **4 trials**; RSI EMA 12 and SMA 29 fixed.

## Ambiguities resolved

- Level entry. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
