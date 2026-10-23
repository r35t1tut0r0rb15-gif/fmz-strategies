# #434449 BB Percentage Index Trend Fading Strategy -> `fmz_434449_rsi14_bollinger_band_red_bar_first_green_exit_long`

- FMZ source id: 434449 (lineage).
- Source: https://www.fmz.com/strategy/434449 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-06 14:43:39). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI Bollinger-band reversals with a first-green-bar exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Lot = equity / close x 100 %, pyramiding 100 (adds), not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21] x `mult` [2.0, 1.5]: **4 trials**; band stdev 50.

## Ambiguities resolved

- Adds while long are sizing (one position). Volume not used (MFI off). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_threshold"`.

## Marks

`none`
