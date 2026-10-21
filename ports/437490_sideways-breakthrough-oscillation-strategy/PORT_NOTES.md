# #437490 Sideways Breakthrough Oscillation Strategy -> `fmz_437490_keltner_open_band_cross`

- FMZ source id: 437490 (lineage).
- Source: https://www.fmz.com/strategy/437490 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-03 11:29:24). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C100). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR-width channel |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `mult` [4.0, 2.5]: **4 trials**; source open and true range fixed.

## Ambiguities resolved

- Either-direction crossings; closes repeat the opposite entries. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
