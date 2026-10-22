# #476252 Multi Indicator Trend Crossing Strategy Bull Market Support Band Trading System -> `fmz_476252_weekly_sma20_ema21_band_cross_long`

- FMZ source id: 476252 (lineage).
- Source: https://www.fmz.com/strategy/476252 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-27 14:35:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C230). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly values from completed weeks |
| 2 | PASS | Weekly SMA / EMA band crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported; commission / slippage not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_length` [20, 10] x `ema_length` [21, 30]: **4 trials**.

## Ambiguities resolved

- gaps_on not followed: consecutive weekly values are compared (as written on TradingView the crossover could never fire).
- Weekly values from the last completed broker week. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
