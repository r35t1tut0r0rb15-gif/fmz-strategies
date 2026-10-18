# #436214 Cloud Nebula Dual Moving Average Breakthrough Strategy -> `fmz_436214_high_low_cloud_cross`

- FMZ source id: 436214 (lineage).
- Source: https://www.fmz.com/strategy/436214 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-22 11:48:28). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C87). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; exits on closes |
| 2 | PASS | Cloud crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`c1` [60, 30] x `c2` [240, 120]: **4 trials**.

## Ambiguities resolved

- Stored stop level from the latest entry signal; orders in call order. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
