# #437655 Volume Energy Driven Strategy -> `fmz_437655_bull_bear_volume_share_zone_start_reversal`

- FMZ source id: 437655 (lineage).
- Source: https://www.fmz.com/strategy/437655 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-04 15:38:54). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bullish / bearish volume share zones |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 10000 cash per trade, capital 10000, commission 0.04 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma` [11, 20] x `delta` [15.0, 10.0]: **4 trials**.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_state"`.

## Marks

`none`
