# #439373 量化策略之MA强弱趋势追踪Quantitative-Strategy-of-MA-Strength-Trend-Tracking -> `fmz_439373_ema_alignment_score_hma_cross_long`

- FMZ source id: 439373 (lineage).
- Source: https://www.fmz.com/strategy/439373 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-19 16:50:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C121). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA alignment score and its HMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [10, 20] x `index_period` [200, 100]: **4 trials**; the EMA ladder and weights fixed.

## Ambiguities resolved

- Long direction only (short entries close). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
