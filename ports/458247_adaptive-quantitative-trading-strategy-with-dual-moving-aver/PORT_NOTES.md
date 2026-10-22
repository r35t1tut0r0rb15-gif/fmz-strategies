# #458247 Adaptive Quantitative Trading Strategy with Dual Moving Average Crossover and Take Profit Stop Loss -> `fmz_458247_sma50_200_cross_pct_bracket_reversal`

- FMZ source id: 458247 (lineage).
- Source: https://www.fmz.com/strategy/458247 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 11:41:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C204). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the fill-price bracket as fixed fractions |
| 2 | PASS | SMA crossings with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [50, 20] x `long_len` [200, 100] x `tp_pct` [0.02, 0.05]: **8 trials**; the 1 % stop fixed.

## Ambiguities resolved

- Bracket from the fill bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
