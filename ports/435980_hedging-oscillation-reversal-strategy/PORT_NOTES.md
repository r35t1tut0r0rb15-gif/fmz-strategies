# #435980 Hedging Oscillation Reversal Strategy -> `fmz_435980_band_envelope_counter_trend`

- FMZ source id: 435980 (lineage).
- Source: https://www.fmz.com/strategy/435980 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-20 15:43:18). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C84). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bands, envelope, ADX and stochastic |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 30] x `percent` [1.0, 2.0]: **4 trials**; ADX 14, stochastic 50 / 20 and 2 sd fixed.

## Ambiguities resolved

- Loose exit tests as written; orders in call order. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
