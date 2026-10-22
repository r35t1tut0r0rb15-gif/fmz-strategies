# #442387 Donchian Adaptive Moving Average Trading System -> `fmz_442387_ma_atr_band_breakout_reversal`

- FMZ source id: 442387 (lineage).
- Source: https://www.fmz.com/strategy/442387 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-21 15:08:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C155). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MA band breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_period` [20, 50] x `band_factor` [1.0, 2.0]: **4 trials**; short period 5 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
