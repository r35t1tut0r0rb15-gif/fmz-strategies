# #489157 20均线趋势突破量化交易策略-EMA-20-Breakout-Trend-Following-Quantitative-Trading-Strategy -> `fmz_489157_close_ema20_cross_long`

- FMZ source id: 489157 (lineage).
- Source: https://www.fmz.com/strategy/489157 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-02 11:31:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C270). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close / EMA crossings |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`emaLength` [20, 10, 50]: **3 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days). MPL 2.0.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
