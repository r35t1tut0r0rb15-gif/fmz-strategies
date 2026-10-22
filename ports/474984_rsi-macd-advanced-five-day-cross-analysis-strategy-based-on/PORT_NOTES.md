# #474984 基于RSI和MACD的五日内交叉灵活入场策略优化版本研究-Advanced-Five-Day-Cross-Analysis-Strategy-Based-on-RSI-and-MACD-Integration -> `fmz_474984_rsi5bar_extreme_after_macd_cross_pct_bracket_reversal`

- FMZ source id: 474984 (lineage).
- Source: https://www.fmz.com/strategy/474984 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-13 12:01:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C228). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the average-price bracket as fixed fractions |
| 2 | PASS | RSI-extreme windows after MACD crossings with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (all lengths, levels and percents are constants).

## Ambiguities resolved

- The MACD flags never reset, as written; the long wins ties. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`
