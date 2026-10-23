# #426394 CMF Momentum Breakthrough Moving Average Strategy -> `fmz_426394_cmf_velocity_zero_cross_ema200_atr2_4_bracket_reversal`

- FMZ source id: 426394 (lineage).
- Source: https://www.fmz.com/strategy/426394 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-11 17:40:54). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket from the signal close |
| 2 | PASS | Money-flow velocity zero crossings with an EMA 200 side filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cmf_period` [11, 20] x `atr_mult` [2.0, 3.0]: **4 trials**; velocity 7, EMA 200, ratio 2.

## Ambiguities resolved

- Exit levels fixed at the signal close; a repeat signal's new levels are not followed. Volume = broker tick volume.
- REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "money_flow"`.

## Marks

`trailing_stop_pending`
