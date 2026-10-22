# #444977 Bollinger Bands RSI Combination Strategy -> `fmz_444977_band_reentry_rsi_extreme_reversal`

- FMZ source id: 444977 (lineage).
- Source: https://www.fmz.com/strategy/444977 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-15 16:28:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C171). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band re-entry crossings with RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `rsi_length` [14, 7]: **4 trials**; the multiplier and the RSI levels fixed.

## Ambiguities resolved

- Cancels never act on market orders. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
