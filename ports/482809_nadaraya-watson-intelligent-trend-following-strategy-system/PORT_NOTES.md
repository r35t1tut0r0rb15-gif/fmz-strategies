# #482809 基于Nadaraya-Watson核估计和移动平均交叉的智能趋势跟踪策略系统-Intelligent-Trend-Following-Strategy-System-Based-on-Nadaraya-Watson-Kernel-Estimation-and-Moving-Average-Crossover -> `fmz_482809_nadaraya_watson_sma_cross_always_in`

- FMZ source id: 482809 (lineage).
- Source: https://www.fmz.com/strategy/482809 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:54:41). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A kernel smoothing and an SMA of it. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bandwidth` [8, 4] x `lookback` [15, 30]: **4 trials**; defaults 8 / 15 (the source's); the 500-bar window fixed.

## Ambiguities resolved

- The kernel uses past closes only (lags 0-499), so it is not the repainting centred Nadaraya-Watson; it is na until
  500 bars exist, as written (`close[i]` na before the first bar makes the sum na).
- `inPosition` alternates the signals: a short cross before the first long is ignored; then every cross reverses.
  REVERSAL INTENDED (always in). Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
