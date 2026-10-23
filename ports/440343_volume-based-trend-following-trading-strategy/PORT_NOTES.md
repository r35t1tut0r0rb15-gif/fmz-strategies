# #440343 Volume based Trend Following Trading Strategy -> `fmz_440343_volume_ratio_surge_state_close13_1h_long_only`

- FMZ source id: 440343 (lineage).
- Source: https://www.fmz.com/strategy/440343 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-29 15:04:18). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume-surge state machine with a 13-bar trend test |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, commission 0.075 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vol_length` [34, 20] x `direction` [13, 26]: **4 trials**; smoothing 200, rising 21, falling 13, thresholds 1 / 1.2.

## Ambiguities resolved

- v4 integer division in the ratio as written. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_state"`.

## Marks

`none`
