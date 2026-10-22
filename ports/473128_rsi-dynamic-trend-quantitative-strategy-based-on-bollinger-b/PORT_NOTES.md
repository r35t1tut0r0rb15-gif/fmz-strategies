# #473128 基于布林带和RSI交叉的动态趋势量化策略-Dynamic-Trend-Quantitative-Strategy-Based-on-Bollinger-Bands-and-RSI-Cross -> `fmz_473128_bb20_band_reentry_rsi_confirm_long`

- FMZ source id: 473128 (lineage).
- Source: https://www.fmz.com/strategy/473128 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 14:49:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C213). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band re-entries with RSI confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `rsi_len` [14, 7]: **4 trials**; the band width and RSI levels fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
