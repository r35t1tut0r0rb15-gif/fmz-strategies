# #489189 TrendSync-Pro-SMC-多时间框架趋势跟随策略-TrendSync-Pro-SMC-Multi-Timeframe-Trend-Following-Strategy -> `fmz_489189_pivot_trendline_cross_flat_bracket`

- FMZ source id: 489189 (lineage).
- Source: https://www.fmz.com/strategy/489189 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-02 15:42:17). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; pivots confirmed after their right bars; bracket fixed at entry. |
| 2 | PASS | Pivot levels and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trend_period` [20, 10] x `tp_pct` [2.0, 4.0]: **4 trials**; defaults 20 / 2 (the source's); SL 1 % fixed.

## Ambiguities resolved

- The "60" security on the 1-hour chart is the bar's own close; the filter is an up / down close.
- Entries only from flat: simulate() follows the house bracket on bars; the level crosses are close-checked exits,
  from the fill bar. A pivot low written after a pivot high on the same bar wins. Opposite entries cannot occur.
- FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
