# #439089 基于ATR波动性与HMA趋势偏差的双均线突破策略Baseline-Cross-Qualifier-ATR-Volatility-HMA-Trend-Bias-Mean-Reversion-Strategy -> `fmz_439089_baseline_qualifier_hma_bias`

- FMZ source id: 439089 (lineage).
- Source: https://www.fmz.com/strategy/439089 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-17 16:37:23). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C116). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Baseline distance, Hull bias; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`baseline_len` [20, 50] x `qualifier_mult` [0.5, 1.0]: **4 trials**; ATR 14, HMA 50 and the 3-bar qualifier fixed.

## Ambiguities resolved

- Same low test for shorts as written; per-bar bracket pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop_pending`
