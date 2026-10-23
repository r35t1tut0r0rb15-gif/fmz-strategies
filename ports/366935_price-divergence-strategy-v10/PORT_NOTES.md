# #366935 Price Divergence Strategy v10 -> `fmz_366935_macd_hist_fractal_divergence_mmlo_quadrant_reversal`

- FMZ source id: 366935 (lineage).
- Source: https://www.fmz.com/strategy/366935 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-31 18:31:45). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD-histogram divergences with a Donchian oscillator filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity and capital 10000 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 50] x `quad` [2, 1]: **4 trials**; MACD 12 / 26 / 9 (SMA lines, EMA signal).

## Ambiguities resolved

- Volume not used (method 1). The trail without an offset places nothing (as #441084). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
