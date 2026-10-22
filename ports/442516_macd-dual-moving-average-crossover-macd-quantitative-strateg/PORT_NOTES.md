# #442516 MACD量化策略之双重叉叉均线突破策略Dual-Moving-Average-Crossover-MACD-Quantitative-Strategy -> `fmz_442516_macd_cross_zero_side_sma200_pct_bracket`

- FMZ source id: 442516 (lineage).
- Source: https://www.fmz.com/strategy/442516 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-22 15:32:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C156). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed from the fill |
| 2 | PASS | MACD crossings with an SMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Margin settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [0.02, 0.04] x `ma_len` [200, 100]: **4 trials**; the stop fraction and the MACD lengths fixed.

## Ambiguities resolved

- Bracket from the fill bar as fixed fractions. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
