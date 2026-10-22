# #471688 双均线RSI趋势动量策略-Dual-Moving-Average-RSI-Trend-Momentum-Strategy -> `fmz_471688_rsi_extreme_with_sma10_50_trend_reversal`

- FMZ source id: 471688 (lineage).
- Source: https://www.fmz.com/strategy/471688 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 14:34:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C209). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI extremes with the SMA trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [10, 20] x `long_len` [50, 100] x `rsi_len` [14, 7]: **8 trials**.

## Ambiguities resolved

- Call order followed (entries, then closes). REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
