# #449810 Hurst Future Lines of Demarcation Strategy -> `fmz_449810_hurst_fld_state_cross_reversal`

- FMZ source id: 449810 (lineage).
- Source: https://www.fmz.com/strategy/449810 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-29 13:58:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C180). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the FLDs are past values |
| 2 | PASS | FLD state machine crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cyc_q` [5, 10] x `cyc` [20, 40]: **4 trials**; the trend cycle 80 fixed.

## Ambiguities resolved

- FLD = shifted ohlc4 (smoothing off). REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "cycle_filter"`.

## Marks

`none`
