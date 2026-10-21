# #437801 RSI和MACD结合支撑阻力的量化交易策略Quantitative-Trading-Strategy-Combining-RSI-MACD-and-Support-Resistance -> `fmz_437801_macd_cross_rsi_near_sr`

- FMZ source id: 437801 (lineage).
- Source: https://www.fmz.com/strategy/437801 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-05 16:24:58). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C106). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings, RSI levels and rolling extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`near_frac` [0.01, 0.005] x `fast` [12, 8]: **4 trials**; MACD slow 26 / signal 9, RSI 14 at 30 / 70 and the 100-bar window fixed.

## Ambiguities resolved

- Current bar inside the 100-bar extremes. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
