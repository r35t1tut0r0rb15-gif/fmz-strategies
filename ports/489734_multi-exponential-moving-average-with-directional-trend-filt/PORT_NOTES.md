# #489734 Multi Exponential Moving Average with Directional Trend Filter Trading System -> `fmz_489734_ema5_8_cross_ema13_exit_reversal`

- FMZ source id: 489734 (lineage).
- Source: https://www.fmz.com/strategy/489734 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-08 10:13:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C272). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with an EMA exit |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Capital 1000, 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 3] x `slow` [8, 13]: **4 trials**; exit EMA 13.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h". MPL 2.0.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
