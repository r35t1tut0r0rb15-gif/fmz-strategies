# #431267 Big Surge Big Fall Strategy -> `fmz_431267_big_bar_fade`

- FMZ source id: 431267 (lineage).
- Source: https://www.fmz.com/strategy/431267 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-06 15:48:22). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Range and body ratios |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [10, 20] x `mult` [2.0, 3.0]: **4 trials**; body share 0.5 fixed.

## Ambiguities resolved

- SL / TP option off (default). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_spike_reversal"`.

## Marks

`none`
