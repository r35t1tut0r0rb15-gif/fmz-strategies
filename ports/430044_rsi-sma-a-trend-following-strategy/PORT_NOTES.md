# #430044 基于RSI极值与SMA均线过滤的趋势跟踪策略A-Trend-Following-Strategy -> `fmz_430044_rsi_extremes_sma200_stop`

- FMZ source id: 430044 (lineage).
- Source: https://www.fmz.com/strategy/430044 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-24 14:47:38). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; a fixed percentage stop. |
| 2 | PASS | RSI levels, a moving average and a percentage stop. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 36,000 cash order size stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG430044. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `sl_pct` [5.0, 3.0]: **4 trials**; SMA 200 and the RSI levels 45 / 65 / 75 / 25 fixed.

## Ambiguities resolved

- close_all closes either side. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop`
