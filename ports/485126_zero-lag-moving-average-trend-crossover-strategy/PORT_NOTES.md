# #485126 Zero Lag Moving Average Trend Crossover Strategy -> `fmz_485126_zlema15_ema15_cross_long`

- FMZ source id: 485126 (lineage).
- Source: https://www.fmz.com/strategy/485126 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-06 11:06:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C263). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Zero-lag EMA crossings |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [15, 30, 50]: **3 trials**.

## Ambiguities resolved

- The EOD close cannot fire on hourly bars, as written. MPL 2.0 source, ported and stated. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
