# #434301 Volume driven Oscillation Quant Strategy -> `fmz_434301_klinger_volume_oscillator_trigger_state_daily_reversal`

- FMZ source id: 434301 (lineage).
- Source: https://www.fmz.com/strategy/434301 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-05 11:35:50). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume oscillator against its trigger |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_x` [34, 20] x `slow_x` [55, 89]: **4 trials**; trigger 13.

## Ambiguities resolved

- Volume = broker tick volume (Klinger). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_state"`.

## Marks

`none`
