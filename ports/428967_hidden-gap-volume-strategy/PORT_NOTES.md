# #428967 Hidden Gap Volume Strategy -> `fmz_428967_volume_vs_sma20_state_reversal`

- FMZ source id: 428967 (lineage).
- Source: https://www.fmz.com/strategy/428967 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-11 14:44:26). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume against its average as a state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_ma` [20, 50]: **2 trials**.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_state"`.

## Marks

`none`
