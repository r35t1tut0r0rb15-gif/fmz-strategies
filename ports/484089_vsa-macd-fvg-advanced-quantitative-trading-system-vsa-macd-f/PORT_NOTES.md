# #484089 多维度量化交易系统高级VSA-MACD-FVG策略分析与优化框架-Advanced-Quantitative-Trading-System-VSA-MACD-FVG-Strategy-Analysis-and-Optimization-Framework -> `fmz_484089_vsa_macd_fvg_overlap_1h_reversal`

- FMZ source id: 484089 (lineage).
- Source: https://www.fmz.com/strategy/484089 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-28 09:39:23). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume-spread breakouts with MACD momentum inside fair-value gaps |
| 3 | PASS | Exchange pair in the header only (TRUMP_USDT). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`price_lb` [5, 10] x `fvg_lb` [2, 3]: **4 trials**; MACD 12 / 26 / 9, volume SMA 20.

## Ambiguities resolved

- Gap levels start at 0 and persist. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "gap"`.

## Marks

`none`
