# #428100 Clear Trend Tracking Strategy -> `fmz_428100_wavetrend_cross`

- FMZ source id: 428100 (lineage).
- Source: https://www.fmz.com/strategy/428100 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-28 16:07:12). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Equity-based order size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n1` [9, 10] x `n2` [12, 21]: **4 trials**; defaults 9 / 12 (the source's).

## Ambiguities resolved

- Only the WaveTrend cross reaches the orders; the rest is drawn (the VWMA option is off).
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "wavetrend"`.

## Marks

`none`
