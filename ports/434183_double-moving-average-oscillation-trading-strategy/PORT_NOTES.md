# #434183 Double Moving Average Oscillation Trading Strategy -> `fmz_434183_combo_2_20_ema_apz`

- FMZ source id: 434183 (lineage).
- Source: https://www.fmz.com/strategy/434183 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-04 15:28:12). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C65). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average and range-band relations |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28] x `band_pct` [2.0, 1.5]: **4 trials**; APZ periods 20 fixed.

## Ambiguities resolved

- APZ state undefined until its first signal, as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
