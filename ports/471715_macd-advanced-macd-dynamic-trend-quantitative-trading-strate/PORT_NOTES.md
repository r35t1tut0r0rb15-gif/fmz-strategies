# #471715 MACD动态趋势量化交易策略进阶版-Advanced-MACD-Dynamic-Trend-Quantitative-Trading-Strategy -> `fmz_471715_macd_menu_cross_long`

- FMZ source id: 471715 (lineage).
- Source: https://www.fmz.com/strategy/471715 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 16:27:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C211). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`setting` [0, 1, 2]: **3 trials** (menu entries Standard 12 / 26 / 9, Short-Term 5 / 35 / 5, Forex 8 / 17 / 9 of the source).

## Ambiguities resolved

- Default MACD setting (12, 26, 9). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
