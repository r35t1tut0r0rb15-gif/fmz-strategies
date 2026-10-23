# #484579 量化交易VSA体积分析与MACD动量指标结合公平价值缺口策略-Quantitative-Trading-Strategy-Combining-VSA-Volume-Analysis-MACD-Momentum-Indicator-and-Fair-Value-Gap-Detection -> `fmz_484579_vsa_macd_fvg3_overlap_reversal`

- FMZ source id: 484579 (lineage).
- Source: https://www.fmz.com/strategy/484579 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-03 09:52:54). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume-spread breakouts with MACD momentum inside fair-value gaps |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`price_lb` [5, 10] x `fvg_lb` [3, 2]: **4 trials**; MACD 12 / 26 / 9, volume SMA 20.

## Ambiguities resolved

- Gap levels start at 0 and persist. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "gap"`.

## Marks

`none`
