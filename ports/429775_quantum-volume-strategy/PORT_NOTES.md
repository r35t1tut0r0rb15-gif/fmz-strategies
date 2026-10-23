# #429775 Quantum Volume Strategy -> `fmz_429775_volume_sma_ratio_threshold_cross_reversal`

- FMZ source id: 429775 (lineage).
- Source: https://www.fmz.com/strategy/429775 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-20 16:28:44). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume-average jump crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`qv_period` [14, 5] x `qv_threshold` [1.5, 1.2]: **4 trials**.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_state"`.

## Marks

`none`
