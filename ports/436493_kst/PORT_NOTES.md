# #436493 KST策略 -> `fmz_436493_kst_signal_cross`

- FMZ source id: 436493 (lineage).
- Source: https://www.fmz.com/strategy/436493 (PineScript v4, author 镜花水月、, FMZ last
  modified 2023-12-26 11:25:30). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C90). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Rate-of-change crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`roc1` [10, 8] x `sig` [9, 5]: **4 trials**; the other rates and smoothings fixed.

## Ambiguities resolved

- ta. prefix in a version 4 header, read as the crossing. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
