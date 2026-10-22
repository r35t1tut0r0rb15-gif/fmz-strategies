# #444968 Bollinger Bands and Fibonacci Retracement Strategy -> `fmz_444968_band_reentry_cross_reversal`

- FMZ source id: 444968 (lineage).
- Source: https://www.fmz.com/strategy/444968 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-15 15:46:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C171). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band re-entry crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 1.5]: **4 trials**.

## Ambiguities resolved

- Cancels never act on market orders. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
