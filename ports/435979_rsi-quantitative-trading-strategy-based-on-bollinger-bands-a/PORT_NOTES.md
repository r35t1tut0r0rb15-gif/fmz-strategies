# #435979 基于布林带和RSI的量化交易策略Quantitative-Trading-Strategy-Based-on-Bollinger-Bands-and-RSI -> `fmz_435979_daily_bollinger_rsi_fade`

- FMZ source id: 435979 (lineage).
- Source: https://www.fmz.com/strategy/435979 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-20 15:39:19). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C84). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; higher-timeframe bands from completed days |
| 2 | PASS | Bands, RSI and percent rules |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity-based quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 30] x `take_profit` ["Central", "Opposite"]: **4 trials**; RSI 14 at 30 / 70 and the 2 % stop fixed.

## Ambiguities resolved

- Daily bands of the last completed day; close-based take profit / stop. Opposite entries cannot occur. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
