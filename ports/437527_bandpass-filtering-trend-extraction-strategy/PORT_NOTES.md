# #437527 Bandpass Filtering Trend Extraction Strategy -> `fmz_437527_bandpass_trend_sign_state`

- FMZ source id: 437527 (lineage).
- Source: https://www.fmz.com/strategy/437527 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-03 15:22:49). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C101). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band-pass sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430069. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `delta` [0.5, 0.3]: **4 trials**; trigger 0 fixed; reverse off.

## Ambiguities resolved

- 3.1415 as pi as written; state entries. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "cycle_filter"`.

## Marks

`none`
