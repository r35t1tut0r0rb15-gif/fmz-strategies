# #433966 Multi Take Profit and Stop Loss WaveTrend Trend Following Strategy -> `fmz_433966_wavetrend_extreme_cross`

- FMZ source id: 433966 (lineage).
- Source: https://www.fmz.com/strategy/433966 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-01 18:09:12). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C64). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator crosses at levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`level` [60, 53] x `n1` [10, 20]: **4 trials**; average 21 fixed (53 is the author's level 2).

## Ambiguities resolved

- Filters off by default. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
