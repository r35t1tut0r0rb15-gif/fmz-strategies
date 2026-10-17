# #433079 Detrended Price Oscillator Quantitative Trading Strategy -> `fmz_433079_close_vs_sma_state`

- FMZ source id: 433079 (lineage).
- Source: https://www.fmz.com/strategy/433079 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-24 11:22:30). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C58). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | The close against its own average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND433079. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28, 50]: **3 trials**.

## Ambiguities resolved

- Undisplaced SMA as written. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
