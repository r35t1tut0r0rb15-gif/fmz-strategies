# #474972 双移动平均线与MACD结合的趋势跟踪动态止盈智能交易系统-Dual-Moving-Average-and-MACD-Combined-Trend-Following-Dynamic-Take-Profit-Smart-Trading-System -> `fmz_474972_ma50_200_trend_macd_cross_spaced_pip_bracket_from_flat`

- FMZ source id: 474972 (lineage).
- Source: https://www.fmz.com/strategy/474972 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-13 11:23:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C227). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the pip bracket as fixed fractions of the fill |
| 2 | PASS | Trend MACD crossings with close exits and a pip bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_ma` [50, 20] x `slow_ma` [200, 100]: **4 trials**; pips, MACD and spacing fixed.

## Ambiguities resolved

- Pips and the MACD threshold as fractions of 42000. Entries only from flat.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
