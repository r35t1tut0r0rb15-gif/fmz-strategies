# #471713 基于ATR的多重趋势跟踪策略与止盈止损优化系统-ATR-Based-Multi-Trend-Following-Strategy-with-Take-Profit-and-Stop-Loss-Optimization-System -> `fmz_471713_classic_supertrend_flip_up_pct_bracket_long`

- FMZ source id: 471713 (lineage).
- Source: https://www.fmz.com/strategy/471713 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 16:14:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C211). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the fill-price bracket as fixed fractions |
| 2 | PASS | Supertrend flips with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`periods` [10, 14] x `multiplier` [3.0, 2.0] x `tp_pct` [0.05, 0.10]: **8 trials**; the 2 % stop fixed.

## Ambiguities resolved

- Date window dropped; bracket from the fill bar. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`coarse_bar_stop`
