# #440866 Trend Prediction Dual Moving Average Strategy -> `fmz_440866_wavetrend_gap_turn_long`

- FMZ source id: 440866 (lineage).
- Source: https://www.fmz.com/strategy/440866 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-02 17:39:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C141). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | WaveTrend gap slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n1` [10, 20] x `wt_factor` [4, 2]: **4 trials**; average 21 fixed.

## Ambiguities resolved

- Oscillator-versus-price test as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "wavetrend_oscillator"`.

## Marks

`none`
