# #442537 双EMA快慢线交叉策略Dual-EMA-Crossover-Strategy -> `fmz_442537_ema25_50_cross_pct_bracket_long`

- FMZ source id: 442537 (lineage).
- Source: https://www.fmz.com/strategy/442537 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-22 16:18:39). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C157). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Percent-over-tick bracket -> fixed fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital, commission and slippage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [0.02, 0.04] x `fast` [25, 12]: **4 trials**; the stop fraction and the EMA 50 fixed.

## Ambiguities resolved

- Percent-over-tick bracket as fixed fractions of the fill. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
