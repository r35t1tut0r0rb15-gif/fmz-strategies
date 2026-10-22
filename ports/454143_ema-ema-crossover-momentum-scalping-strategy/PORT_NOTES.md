# #454143 EMA交叉动量短线交易策略-EMA-Crossover-Momentum-Scalping-Strategy -> `fmz_454143_ema9_21_cross_fill_bracket_reversal`

- FMZ source id: 454143 (lineage).
- Source: https://www.fmz.com/strategy/454143 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-14 15:24:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C194). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the fill-price bracket as fixed fractions |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.007, 0.02] x `tp_pct` [0.005, 0.02]: **4 trials**; the EMA lengths fixed.

## Ambiguities resolved

- Bracket from the fill bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
