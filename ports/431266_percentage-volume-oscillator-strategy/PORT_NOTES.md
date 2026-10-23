# #431266 Percentage Volume Oscillator Strategy -> `fmz_431266_percentage_volume_oscillator_signal_state_reversal`

- FMZ source id: 431266 (lineage).
- Source: https://www.fmz.com/strategy/431266 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-06 15:45:02). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume oscillator against its signal |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_ema` [12, 5] x `long_ema` [26, 34]: **4 trials**; signal 9.

## Ambiguities resolved

- Rising volume oscillator = short, as written. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_state"`.

## Marks

`none`
