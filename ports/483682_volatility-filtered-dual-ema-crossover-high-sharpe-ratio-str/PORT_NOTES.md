# #483682 Volatility Filtered Dual EMA Crossover High Sharpe Ratio Strategy -> `fmz_483682_ema10_30_cross_atr_over_mean_plus_sd_reversal`

- FMZ source id: 483682 (lineage).
- Source: https://www.fmz.com/strategy/483682 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-25 11:23:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C260). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent close bracket pending |
| 2 | PASS | EMA crossings in high ATR |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-sized quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_fast_length` [10, 5] x `ema_slow_length` [30, 60]: **4 trials**; ATR 14, mean / sd 20.

## Ambiguities resolved

- The bracket re-sent from each bar's close is pending, not ported. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
