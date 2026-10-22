# #442929 Pullback Trading Strategy Based on Dynamic Moving Average -> `fmz_442929_sma280_13_pullback_fill_stop_long`

- FMZ source id: 442929 (lineage).
- Source: https://www.fmz.com/strategy/442929 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 14:38:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C163). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA pullback band; close-vs-fill stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG442929. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_length1` [280, 200] x `ma_length2` [13, 20]: **4 trials**; the band and the stop fixed.

## Ambiguities resolved

- Fill-price stop. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
