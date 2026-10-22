# #473123 AVMQTS Adaptive Volatility and Momentum Quantitative Trading System AVMQTS -> `fmz_473123_alternating_macd8_7_9_cross_momentum_sma50_pct_bracket_reversal`

- FMZ source id: 473123 (lineage).
- Source: https://www.fmz.com/strategy/473123 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 14:20:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C213). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the fill-price bracket as fixed fractions |
| 2 | PASS | Alternating MACD crossings with momentum and SMA filters |
| 3 | PASS | Exchange pair in the header only (ETH named in the title). |
| 4 | DONE | Fixed trade size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`momentum_length` [37, 20] x `tp_pct` [0.09, 0.05] x `sl_pct` [0.099, 0.05]: **8 trials**; the MACD lengths fixed.

## Ambiguities resolved

- First trade long, sides alternate (as written); bracket from the fill bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop`
