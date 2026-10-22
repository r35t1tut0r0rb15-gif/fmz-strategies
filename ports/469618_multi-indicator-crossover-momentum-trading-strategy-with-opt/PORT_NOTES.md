# #469618 Multi Indicator Crossover Momentum Trading Strategy with Optimized Take Profit and Stop Loss System -> `fmz_469618_ema9_21_cross_rsi_macd_confirm_pct_bracket_reversal`

- FMZ source id: 469618 (lineage).
- Source: https://www.fmz.com/strategy/469618 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-10-14 11:45:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C208). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the fill-price bracket as fixed fractions |
| 2 | PASS | EMA crossings with RSI and MACD confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Margin settings stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50] x `tp_pct` [0.03, 0.06]: **8 trials**; the 1 % stop fixed.

## Ambiguities resolved

- Bracket from the fill bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
