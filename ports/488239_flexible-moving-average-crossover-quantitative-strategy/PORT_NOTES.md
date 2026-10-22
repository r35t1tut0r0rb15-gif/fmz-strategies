# #488239 Flexible Moving Average Crossover Quantitative Strategy -> `fmz_488239_sma20_200_cross_reversal`

- FMZ source id: 488239 (lineage).
- Source: https://www.fmz.com/strategy/488239 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-26 11:01:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C265). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fastMAPeriod` [20, 50] x `slowMAPeriod` [200, 100]: **4 trials** (the slow setting moves only the short test).

## Ambiguities resolved

- The long test's SMA 200 is fixed as written. REVERSAL INTENDED. FREQ = "2min". MPL 2.0.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
